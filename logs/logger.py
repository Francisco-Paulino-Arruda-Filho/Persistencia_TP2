import logging
import yaml

# Carrega as configurações do arquivo YAML
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Mapeia a string para o nível correspondente do logging
log_level = getattr(logging, config["logging"]["level"].upper(), logging.INFO)

# Configuração básica de logging
logging.basicConfig(
    level=log_level,
    format=config["logging"]["format"],
    handlers=[
        logging.FileHandler(config["logging"]["file"]),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)