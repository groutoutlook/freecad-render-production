#!/usr/bin/env python3
################################################################################
# File:    freecad-to-png.py
# Version: 0.3
# Purpose: Extracts a png screenshot of a given .FCStd freecad file
# Created: 2024-02-06
# Updated: 2025-11-02
# 
# IMPORTANT: This script must be run with FreeCAD's Python interpreter!
# Usage: freecadcmd freecad-to-png.py <input.FCStd> [-o output.png]
#        Or simply: python freecad-to-png.py <input.FCStd> (auto-relaunches)
################################################################################

import sys
import argparse
import os
import subprocess
import shutil

# Default FreeCAD paths (can be overridden with arguments)
DEFAULT_FREECAD_LIB_PATH = '/usr/lib/freecad-python3/lib'
DEFAULT_FREECAD_MOD_PATH = '/usr/share/freecad/Mod'

################################################################################
#                                  FUNCTIONS                                   #
################################################################################

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Extract a PNG screenshot from a FreeCAD file (.FCStd)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the input .FCStd file'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Path for the output PNG file (default: production/<input-name>.png)'
    )

    parser.add_argument(
        '--freecad-lib-path',
        default=DEFAULT_FREECAD_LIB_PATH,
        help='Path to FreeCAD Python library'
    )
    
    parser.add_argument(
        '--freecad-mod-path', 
        default=DEFAULT_FREECAD_MOD_PATH,
        help='Path to FreeCAD modules'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress FreeCAD warnings and messages during document loading'
    )
    
    # HACK: post parsing..
    args = parser.parse_args()

    if args.output is None:
        input_name = os.path.splitext(os.path.basename(args.input_file))[0]
        args.output = os.path.join('production', f'{input_name}.png')

    return args

def setup_freecad_paths(lib_path, mod_path):
    """Add FreeCAD paths to sys.path."""
    if lib_path and os.path.exists(lib_path):
        sys.path.append(lib_path)
    if mod_path and os.path.exists(mod_path):
        sys.path.append(mod_path)

################################################################################
#                                  MAIN BODY                                   #
################################################################################

def main():
    """Main function to handle the conversion process."""
    
    args = parse_arguments()
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    # Check if input file has correct extension
    if not args.input_file.lower().endswith('.fcstd'):
        print(f"Warning: Input file '{args.input_file}' does not have .FCStd extension.")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Setup FreeCAD paths
    # setup_freecad_paths(args.freecad_lib_path, args.freecad_mod_path)
    
    # Import FreeCAD modules after setting up paths
    try:
        import FreeCAD
        import FreeCADGui
    except ImportError as e:
        print(f"Error: Could not import FreeCAD modules: {e}", file=sys.stderr)
        print("Please ensure FreeCAD is installed and paths are correct.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Save original stdout/stderr
        origStdout = sys.stdout
        origStderr = sys.stderr
        
        # Suppress FreeCAD console output if quiet mode
        if args.quiet:
            import io
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
        
        # showMainWindow() without blocking stderr & stdout https://forum.freecad.org/viewtopic.php?p=493152#p493152
        FreeCADGui.showMainWindow()
        
        # Open the FreeCAD document (warnings about missing Raytracing module will be suppressed in quiet mode)
        FreeCAD.openDocument(str(args.input_file))
        output_png = args.output
        # Restore stdout/stderr
        sys.stdout = origStdout
        sys.stderr = origStderr
        activeView = FreeCADGui.activeView()
        # activeView.setViewportSize(1200, 1200) # this wont work.
        
        # Fit all objects in the view
        # FreeCADGui.SendMsgToActiveView("ViewFit")
        activeView.fitAll()
        activeView.saveImage(output_png, 1080, 1080, 'Transparent')
        
        print(f"Successfully saved screenshot to: {args.output}")
        
    except Exception as e:
        # Make sure to restore stdout/stderr in case of error
        sys.stdout = origStdout
        sys.stderr = origStderr
        print(f"Error processing file: {e}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()

