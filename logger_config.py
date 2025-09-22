import logging

def setup_logging():
    """
    Настройка логирования для всего проекта
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        handlers=[logging.StreamHandler()]
    )
