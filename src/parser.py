import json
import pandas as pd
import geopandas as gpd
from pathlib import Path
import logging

logger = logging.getLogger("Parser")

def _json_serializer(obj):
    """Função customizada para converter objetos pandas/numpy/datetime em string no JSON."""
    if isinstance(obj, (pd.Timestamp, pd.Timedelta)):
        return obj.isoformat()
    if pd.isna(obj):
        return None
    return str(obj)

class DatasetParser:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.metadata_map = {}
        self._load_dictionaries()

    def _load_dictionaries(self):
        """Carrega todos os arquivos JSON de dicionário/metadados para contextualizar outros arquivos."""
        json_files = list(self.data_dir.glob("*.json"))
        for jf in json_files:
            try:
                with open(jf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "metadados" in data:
                        meta = data["metadados"]
                        header = meta.get("cabecalho", {})
                        title = header.get("titulo", jf.stem)
                        fields = meta.get("campos", [])
                        
                        self.metadata_map[jf.name] = {
                            "title": title,
                            "description": header.get("descricao", ""),
                            "tags": header.get("etiquetas", ""),
                            "fields": fields
                        }
            except Exception as e:
                logger.warning(f"Erro ao ler JSON {jf.name}: {e}")

    def parse_file(self, file_path: Path):
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext == ".json":
            return self._parse_json(path)
        elif ext == ".csv":
            return self._parse_csv(path)
        elif ext == ".geojson":
            return self._parse_geojson(path)
        else:
            return []

    def _parse_json(self, path: Path):
        chunks = []
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                
            if "metadados" in data:
                meta = data["metadados"]
                header = meta.get("cabecalho", {})
                title = header.get("titulo", path.stem)
                desc = header.get("descricao", "")
                tags = header.get("etiquetas", "")
                resp = header.get("responsavel_dados", "")
                
                fields_str_list = []
                for field in meta.get("campos", []):
                    code = field.get("codigo", "")
                    fdesc = field.get("descricao", "")
                    ftype = field.get("tipo", "")
                    fields_str_list.append(f"- Campo '{code}' ({ftype}): {fdesc}")
                
                content = (
                    f"DICIONÁRIO DE DADOS E METADADOS\n"
                    f"Arquivo Fonte: {path.name}\n"
                    f"Título do Conjunto: {title}\n"
                    f"Descrição: {desc}\n"
                    f"Etiquetas / Palavras-chave: {tags}\n"
                    f"Órgão Responsável: {resp}\n"
                    f"Esquema e Descrição de Campos:\n" + "\n".join(fields_str_list)
                )
                
                chunks.append({
                    "file_name": path.name,
                    "data_type": "json_metadados",
                    "dataset_title": title,
                    "chunk_index": 0,
                    "content": content,
                    "metadata": {"tags": tags, "fields_count": len(fields_str_list)}
                })
            else:
                content = f"CONTEÚDO ESTRUTURADO JSON ({path.name}):\n" + json.dumps(data, ensure_ascii=False, indent=2, default=_json_serializer)[:3000]
                chunks.append({
                    "file_name": path.name,
                    "data_type": "json_generic",
                    "dataset_title": path.stem,
                    "chunk_index": 0,
                    "content": content,
                    "metadata": {}
                })
        except Exception as e:
            logger.error(f"Erro ao processar JSON {path.name}: {e}")
            
        return chunks

    def _parse_csv(self, path: Path):
        chunks = []
        try:
            for encoding in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(path, sep=None, engine='python', encoding=encoding, nrows=5000)
                    break
                except Exception:
                    continue
            else:
                return []

            title = path.stem
            columns = list(df.columns)
            total_rows = len(df)
            
            summary_content = (
                f"TABELA DE DADOS CSV: {path.name}\n"
                f"Título/Assunto: {title}\n"
                f"Total de Linhas Analisadas: {total_rows}\n"
                f"Colunas Presentes: {', '.join(map(str, columns))}\n"
                f"Amostra dos Primeiros Registros:\n"
                f"{df.head(5).to_string(index=False)}"
            )
            chunks.append({
                "file_name": path.name,
                "data_type": "csv_summary",
                "dataset_title": title,
                "chunk_index": 0,
                "content": summary_content,
                "metadata": {"columns": columns, "total_rows": total_rows}
            })
            
            batch_size = 25
            for i in range(0, min(total_rows, 1000), batch_size):
                sub_df = df.iloc[i:i+batch_size]
                rows_text = []
                for _, row in sub_df.iterrows():
                    row_pairs = [f"{col}: {val}" for col, val in row.items() if pd.notna(val) and str(val).strip() != '']
                    rows_text.append(" | ".join(row_pairs))
                
                chunk_content = (
                    f"REGISTROS DA TABELA ({path.name}) [Linhas {i+1} a {i+len(sub_df)}]:\n"
                    + "\n".join(rows_text)
                )
                chunks.append({
                    "file_name": path.name,
                    "data_type": "csv_data",
                    "dataset_title": title,
                    "chunk_index": len(chunks),
                    "content": chunk_content,
                    "metadata": {"row_start": i+1, "row_end": i+len(sub_df)}
                })

        except Exception as e:
            logger.error(f"Erro ao processar CSV {path.name}: {e}")

        return chunks

    def _parse_geojson(self, path: Path):
        chunks = []
        try:
            gdf = gpd.read_file(path)
            title = path.stem
            total_features = len(gdf)
            columns = [c for c in gdf.columns if c != 'geometry']
            
            summary_content = (
                f"BASE DE DADOS GEOGRÁFICA GEOJSON: {path.name}\n"
                f"Título/Assunto: {title}\n"
                f"Quantidade de Feições/Objetos Espaciais: {total_features}\n"
                f"Atributos/Propriedades da Base: {', '.join(columns)}\n"
            )
            
            if total_features > 0:
                sample_props = gdf[columns].head(3).to_dict(orient='records')
                summary_content += f"\nAmostra de Feições Espaciais:\n{json.dumps(sample_props, ensure_ascii=False, indent=2, default=_json_serializer)}"

            chunks.append({
                "file_name": path.name,
                "data_type": "geojson_summary",
                "dataset_title": title,
                "chunk_index": 0,
                "content": summary_content,
                "metadata": {"total_features": total_features, "attributes": columns}
            })

            batch_size = 15
            for i in range(0, min(total_features, 500), batch_size):
                sub_gdf = gdf.iloc[i:i+batch_size]
                feat_texts = []
                for _, row in sub_gdf.iterrows():
                    props = {k: v for k, v in row.items() if k != 'geometry' and pd.notna(v)}
                    prop_str = ", ".join([f"{k}='{v}'" for k, v in props.items()])
                    feat_texts.append(f"- Objeto {i}: {prop_str}")

                chunk_content = (
                    f"DADOS GEOGRÁFICOS E ATRIBUTOS URBANOS ({path.name}) [Feições {i+1} a {i+len(sub_gdf)}]:\n"
                    + "\n".join(feat_texts)
                )

                chunks.append({
                    "file_name": path.name,
                    "data_type": "geojson_data",
                    "dataset_title": title,
                    "chunk_index": len(chunks),
                    "content": chunk_content,
                    "metadata": {"feature_start": i+1, "feature_end": i+len(sub_gdf)}
                })

        except Exception as e:
            logger.error(f"Erro ao processar GeoJSON {path.name}: {e}")

        return chunks
