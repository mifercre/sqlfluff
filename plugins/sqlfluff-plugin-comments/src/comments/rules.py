from sqlfluff.core.plugin import hookimpl
from sqlfluff.core.rules.base import (
    BaseRule,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)
from typing import List, Optional
import os.path
from sqlfluff.core.config import ConfigLoader


@hookimpl
def get_rules() -> List[BaseRule]:
    """Get plugin rules."""
    return [Rule_Comments_L001]


@hookimpl
def load_default_config() -> dict:
    """Loads the default configuration for the plugin."""
    return ConfigLoader.get_global().load_default_config_file(
        file_dir=os.path.dirname(__file__),
        file_name="plugin_default_config.cfg",
    )


@hookimpl
def get_configs_info() -> dict:
    """Get rule config validations and descriptions."""
    return {}


# These two decorators allow plugins
# to be displayed in the sqlfluff docs
@document_fix_compatible
@document_configuration
class Rule_Comments_L001(BaseRule):
    """CREATE TABLE|VIEW statements should be preceded by a comment section

    | **Anti-pattern**
    | Use CREATE TABLE|VIEW without any documentation about the table .

    .. code-block:: sql

        CREATE TABLE foo
        SELECT a, MAX(b)
        FROM bar
        GROUP BY a
        HAVING MAX(b) > 10

    | **Best practice**
    | Write a comment right before creating the table|view

    .. code-block:: sql
        --
        -- This table keeps, for each `a` the max `b`, as far as `b` is bigger than 10
        --
        CREATE TABLE foo
        SELECT a, MAX(b)
        FROM bar
        GROUP BY a
        HAVING MAX(b) > 10
    """

    def __init__(self, *args, **kwargs):
        """Overwrite __init__ to set config."""
        super().__init__(*args, **kwargs)

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """We should use comments before CREATE TABLE|VIEW."""
        if context.segment.is_type("create_table_statement") or context.segment.is_type("create_view_statement"):
            seg = context.segment
            for seg in context.raw_stack[-2:]:
                if seg.name in ['inline_comment', 'block_comment']:
                    return None

            return [
                LintResult(
                    anchor=seg,
                    description=(
                        "Found CREATE TABLE|VIEW statement without a comment preceding it."
                    ),
                ),
            ]
