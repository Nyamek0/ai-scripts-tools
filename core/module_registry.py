import importlib
import pkgutil
import logging
from pathlib import Path
from fastapi import FastAPI

logger = logging.getLogger(__name__)


class ModuleRegistry:
    """
    Auto-découverte des modules IA.
    Chaque dossier dans /modules/ avec un router.py est automatiquement chargé.
    Pour ajouter un module : créer modules/mon_outil/router.py avec un APIRouter.
    """

    def __init__(self, app: FastAPI):
        self.app = app
        self.modules: dict = {}

    def autodiscover(self):
        modules_path = Path(__file__).parent.parent / "modules"

        if not modules_path.exists():
            logger.warning("Dossier /modules/ introuvable")
            return

        for module_dir in sorted(modules_path.iterdir()):
            if not module_dir.is_dir():
                continue
            if module_dir.name.startswith("_"):
                continue

            router_path = module_dir / "router.py"
            if not router_path.exists():
                continue

            module_name = f"modules.{module_dir.name}.router"
            try:
                mod = importlib.import_module(module_name)

                if not hasattr(mod, "router"):
                    logger.warning(f"⚠️  {module_name} n'expose pas de 'router'")
                    continue

                # Métadonnées optionnelles
                meta = getattr(mod, "MODULE_META", {})
                prefix = meta.get("prefix", f"/{module_dir.name}")
                tags = meta.get("tags", [module_dir.name])

                self.app.include_router(
                    mod.router,
                    prefix=f"/api{prefix}",
                    tags=tags,
                )

                self.modules[module_dir.name] = {
                    "name": meta.get("name", module_dir.name),
                    "description": meta.get("description", ""),
                    "version": meta.get("version", "1.0.0"),
                    "prefix": prefix,
                }

                logger.info(f"✅ Module chargé : {module_dir.name} → /api{prefix}")

            except Exception as e:
                logger.error(f"❌ Erreur chargement module {module_dir.name}: {e}")

        # Endpoint qui liste tous les modules disponibles
        modules_snapshot = dict(self.modules)

        @self.app.get("/api/modules", tags=["registry"])
        async def list_modules():
            return {"modules": modules_snapshot}
