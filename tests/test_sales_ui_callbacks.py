import unittest

from dash import dcc, html

from apps.vndmanuf_sales.ui.sales_tab import SUB_TAB_COMPONENTS
from apps.vndmanuf_sales.ui.sales_tab import layout as sales_layout


class SalesUICallbacksTest(unittest.TestCase):
    def test_sales_layout_has_expected_tabs(self):
        layout = sales_layout()
        self.assertIsInstance(layout, html.Div)
        tabs = next(child for child in layout.children if isinstance(child, dcc.Tabs))
        tab_values = [tab.value for tab in tabs.children]
        expected = list(SUB_TAB_COMPONENTS.keys())
        self.assertEqual(tab_values, expected)


if __name__ == "__main__":
    unittest.main()
