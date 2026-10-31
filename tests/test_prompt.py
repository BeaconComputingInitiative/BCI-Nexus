# BEACON COMPUTING INITIATIVE
# Developer Seal: CJB-DEV-2026
# Component: BCIBot Prompt Reset Test v0.5.2
import unittest
from nexus.gui import _reset_prompt_after_dispatch


class PromptWidget:
    def __init__(self, value):
        self.value = value
        self.focused = False

    def clear(self):
        self.value = ""

    def setFocus(self):
        self.focused = True


class PromptResetTests(unittest.TestCase):
    def test_accepted_prompt_resets_and_refocuses(self):
        prompt = PromptWidget("check my network for endpoints")
        _reset_prompt_after_dispatch(prompt)
        self.assertEqual(prompt.value, "")
        self.assertTrue(prompt.focused)


if __name__ == "__main__":
    unittest.main()
