from importlib import util
from os import path
from glob import glob

routers = []
for module_path in [
    f
    for f in glob(path.join(path.dirname(__file__), "**/*.py"), recursive=True)
    if path.basename(f) != "__init__.py"
]:
    spec = util.spec_from_file_location("", module_path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)

    router = getattr(module, "router", None)
    if router is not None:
        routers.append(router)
