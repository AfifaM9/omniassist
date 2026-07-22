"""
==============================================================================
 OMNIASSIST ENTRY POINT SCRIPT (2026.1)
==============================================================================
 MODEL PRIORITY & FALLBACK HIERARCHY:
   Primary Model:  Gemini 3.5 Flash-Lite
   Fallback 1:     Gemini 3.1 Flash-Lite
   Fallback 2:     Gemini 3 Flash
   Fallback 3:     Gemini 2.5 Flash
   Fallback 4:     Gemini 2.5 Flash-Lite
   Fallback 5:     Gemma 4
   Rule:           Automatically skip deprecated or decommissioned models.
==============================================================================
"""

from interfaces.cli import main

if __name__ == "__main__":
    main()
