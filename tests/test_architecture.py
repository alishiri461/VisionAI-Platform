import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {"fastapi", "starlette", "cv2", "numpy", "PIL", "torch", "onnxruntime"}


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def test_domain_is_framework_and_runtime_independent() -> None:
    for source in (ROOT / "backend/src/visionai/domain").glob("*.py"):
        assert not (imported_roots(source) & FORBIDDEN), source


def test_application_does_not_depend_on_transport_or_infrastructure() -> None:
    for source in (ROOT / "backend/src/visionai/application").rglob("*.py"):
        roots = imported_roots(source)
        assert not (roots & (FORBIDDEN | {"visionai.infrastructure"})), source
