import logging

LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


def setup_logging(level: int = logging.INFO) -> None:
    """Configure le logger racine une seule fois, au démarrage de l'app.
    Chaque module récupère ensuite le sien avec logging.getLogger(__name__)."""
    logging.basicConfig(level=level, format=LOG_FORMAT)
