# Test plan: key_pressed boolean behaviour

This is a pure plan file (not executed). It outlines expected engine behaviour used by unit tests.

- The boolean `key_pressed` is True when any key is currently down, False when none are.
- If multiple keys are pressed, `key_pressed` remains True until all keys are released.
- Key repeat behaviour should not toggle `key_pressed` (repeat generates repeated `key_pressed()` calls, but the boolean stays True).