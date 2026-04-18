from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ManifestLintTests(unittest.TestCase):
    def test_legacy_manifest_lint_rejects_todo_and_accepts_filled_manifest(self):
        module = load_module("legacy-component-skinning/scripts/lint_surface_manifest.py")

        invalid_manifest = """# Skinning Surface Manifest

## Composite Surfaces
| ID | Surface | States To Check | Evidence | Notes |
| --- | --- | --- | --- | --- |
| C1 | toolbar | default / empty | before=`TODO` | TODO |

## Interactive Surfaces
| ID | Trigger Type | Entry | Surface | Evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | click | 编辑 | drawer | before=`TODO` / after=`TODO` | TODO |

## Exception States
| ID | State | Surface | Safe Reproduction | Evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| E1 | validation-error | inline | local submit | normal=`TODO` / exception=`TODO` | TODO |

## Content/Layout Cases
| ID | Surface | Element | Case | Expected | Observed | Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | 筛选栏 | trigger | long label | 主文案可读 | 仅显示前3字 | before=`TODO` / after=`TODO` | TODO |

## Breakpoint Coverage
| ID | Breakpoint | Evidence | Notes |
| --- | --- | --- | --- |
| B1 | desktop | TODO | TODO |

## Unverified Items
| ID | Item | Reason | Next Step |
| --- | --- | --- | --- |
| U1 | TODO | TODO | TODO |

## Exit Checklist
- [ ] all key interactive surfaces enumerated or explicitly marked out of scope
- [ ] content/layout cases checked for primary content, help text, and error copy
- [ ] claims limited to states with real rendered evidence
- [ ] manifest updated with evidence or explicit unverified reasons
"""

        valid_manifest = """# Skinning Surface Manifest

## Composite Surfaces
| ID | Surface | States To Check | Evidence | Notes |
| --- | --- | --- | --- | --- |
| C1 | toolbar | default / empty | before=`toolbar-before.png` / after=`toolbar-after.png` | width stabilized |

## Interactive Surfaces
| ID | Trigger Type | Entry | Surface | Evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | click | 编辑 | drawer | before=`list.png` / after=`drawer.png` | verified end-to-end |

## Exception States
| ID | State | Surface | Safe Reproduction | Evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| E1 | validation-error | inline | local submit | normal=`valid.png` / exception=`invalid.png` | stable reproduction |

## Content/Layout Cases
| ID | Surface | Element | Case | Expected | Observed | Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | 筛选栏 | trigger | long label | 主文案可读 | 面板增宽后完整可读 | before=`narrow.png` / after=`wide.png` | accepted |

## Breakpoint Coverage
| ID | Breakpoint | Evidence | Notes |
| --- | --- | --- | --- |
| B1 | desktop | before=`desktop-before.png` / after=`desktop-after.png` | 1440 verified |

## Unverified Items
| ID | Item | Reason | Next Step |
| --- | --- | --- | --- |
| U1 | 权限不足页面 | 测试账号未开通权限 | QA 提供账号后补回看 |

## Exit Checklist
- [x] all key interactive surfaces enumerated or explicitly marked out of scope
- [x] content/layout cases checked for primary content, help text, and error copy
- [x] claims limited to states with real rendered evidence
- [x] manifest updated with evidence or explicit unverified reasons
"""

        invalid_errors = module.validate_manifest_text(invalid_manifest)
        valid_errors = module.validate_manifest_text(valid_manifest)

        self.assertTrue(invalid_errors)
        self.assertFalse(valid_errors)

    def test_xylink_manifest_lint_rejects_todo_and_accepts_filled_manifest(self):
        module = load_module("xylink-legacy-component-skinning/scripts/lint_surface_manifest.py")

        invalid_errors = module.validate_manifest_text("TODO")
        valid_errors = module.validate_manifest_text(
            """# Skinning Surface Manifest

## Composite Surfaces
| ID | Surface | States To Check | Evidence | Notes |
| --- | --- | --- | --- | --- |
| C1 | 登录页表单 | default / error | before=`a` / after=`b` | ok |

## Interactive Surfaces
| ID | Trigger Type | Entry | Surface | Evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| I1 | click | 登录按钮 | inline error | before=`a` / after=`b` | ok |

## Exception States
| ID | State | Surface | Safe Reproduction | Evidence | Notes |
| --- | --- | --- | --- | --- | --- |
| E1 | backend-unavailable | page-banner | mock | normal=`a` / exception=`b` | ok |

## Content/Layout Cases
| ID | Surface | Element | Case | Expected | Observed | Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | 登录页 | form | long help text | 可读 | 已收敛 | before=`a` / after=`b` | ok |

## Breakpoint Coverage
| ID | Breakpoint | Evidence | Notes |
| --- | --- | --- | --- |
| B1 | desktop | before=`a` / after=`b` | ok |

## Unverified Items
| ID | Item | Reason | Next Step |
| --- | --- | --- | --- |
| U1 | 后端不可用页 | 隔离环境未开放开关 | 待环境可用后补回看 |

## Exit Checklist
- [x] all key interactive surfaces enumerated or explicitly marked out of scope
- [x] content/layout cases checked for primary content, help text, and error copy
- [x] claims limited to states with real rendered evidence
- [x] manifest updated with evidence or explicit unverified reasons
"""
        )

        self.assertTrue(invalid_errors)
        self.assertFalse(valid_errors)

    def test_manifest_lint_requires_core_surface_sections(self):
        module = load_module("legacy-component-skinning/scripts/lint_surface_manifest.py")

        manifest_missing_core_sections = """# Skinning Surface Manifest

## Content/Layout Cases
| ID | Surface | Element | Case | Expected | Observed | Evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L1 | 登录页 | form | long help text | 可读 | 已收敛 | before=`a` / after=`b` | ok |

## Breakpoint Coverage
| ID | Breakpoint | Evidence | Notes |
| --- | --- | --- | --- |
| B1 | desktop | before=`a` / after=`b` | ok |

## Unverified Items
| ID | Item | Reason | Next Step |
| --- | --- | --- | --- |
| U1 | none | fully verified | n/a |

## Exit Checklist
- [x] all key interactive surfaces enumerated or explicitly marked out of scope
- [x] content/layout cases checked for primary content, help text, and error copy
- [x] claims limited to states with real rendered evidence
- [x] manifest updated with evidence or explicit unverified reasons
"""

        errors = module.validate_manifest_text(manifest_missing_core_sections)
        self.assertIn("missing required section: ## Composite Surfaces", errors)
        self.assertIn("missing required section: ## Interactive Surfaces", errors)
        self.assertIn("missing required section: ## Exception States", errors)


if __name__ == "__main__":
    unittest.main()
