import os
import filecmp
import argparse
import json
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import difflib

class DirectoryComparator:
    """Enhanced directory comparison tool with detailed reporting capabilities."""
    
    def __init__(self, dir1: str, dir2: str):
        self.dir1 = Path(dir1).resolve()
        self.dir2 = Path(dir2).resolve()
        self.comparison_time = datetime.datetime.now()
        self.results = {
            'left_only': [],      # Files/dirs only in dir1
            'right_only': [],     # Files/dirs only in dir2
            'diff_files': [],     # Files that differ
            'same_files': [],     # Files that are identical
            'changed_dirs': [],   # Directories with changes
            'file_details': {},   # Detailed file comparison info
            'summary': {}
        }
    
    def compare_directories(self) -> Dict:
        """
        Recursively compares two directories and returns detailed comparison results.
        
        Returns:
            dict: Comprehensive comparison results
        """
        def _compare(d1: Path, d2: Path, rel_path: str = ""):
            comparison = filecmp.dircmp(str(d1), str(d2))
            
            # Track files only in left directory
            for item in comparison.left_only:
                item_path = os.path.join(rel_path, item) if rel_path else item
                full_path = d1 / item
                if full_path.is_file():
                    self.results['left_only'].append({
                        'path': item_path,
                        'type': 'file',
                        'size': full_path.stat().st_size if full_path.exists() else 0,
                        'modified': datetime.datetime.fromtimestamp(full_path.stat().st_mtime).isoformat() if full_path.exists() else None
                    })
                else:
                    self.results['left_only'].append({
                        'path': item_path,
                        'type': 'directory'
                    })
            
            # Track files only in right directory
            for item in comparison.right_only:
                item_path = os.path.join(rel_path, item) if rel_path else item
                full_path = d2 / item
                if full_path.is_file():
                    self.results['right_only'].append({
                        'path': item_path,
                        'type': 'file',
                        'size': full_path.stat().st_size if full_path.exists() else 0,
                        'modified': datetime.datetime.fromtimestamp(full_path.stat().st_mtime).isoformat() if full_path.exists() else None
                    })
                else:
                    self.results['right_only'].append({
                        'path': item_path,
                        'type': 'directory'
                    })
            
            # Track different files
            for item in comparison.diff_files:
                item_path = os.path.join(rel_path, item) if rel_path else item
                file1 = d1 / item
                file2 = d2 / item
                
                file_info = {
                    'path': item_path,
                    'type': 'file',
                    'left_size': file1.stat().st_size if file1.exists() else 0,
                    'right_size': file2.stat().st_size if file2.exists() else 0,
                    'left_modified': datetime.datetime.fromtimestamp(file1.stat().st_mtime).isoformat() if file1.exists() else None,
                    'right_modified': datetime.datetime.fromtimestamp(file2.stat().st_mtime).isoformat() if file2.exists() else None
                }
                
                self.results['diff_files'].append(file_info)
                
                # Get detailed diff for text files
                if self._is_text_file(file1) and self._is_text_file(file2):
                    try:
                        with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
                            diff = list(difflib.unified_diff(
                                f1.readlines(),
                                f2.readlines(),
                                fromfile=f"a/{item_path}",
                                tofile=f"b/{item_path}",
                                lineterm=''
                            ))
                            if diff:
                                self.results['file_details'][item_path] = {
                                    'diff': diff,
                                    'lines_added': len([line for line in diff if line.startswith('+') and not line.startswith('+++')]),
                                    'lines_removed': len([line for line in diff if line.startswith('-') and not line.startswith('---')])
                                }
                    except (UnicodeDecodeError, IOError):
                        self.results['file_details'][item_path] = {'diff': ['Binary file or encoding error']}
            
            # Track same files
            for item in comparison.same_files:
                item_path = os.path.join(rel_path, item) if rel_path else item
                self.results['same_files'].append(item_path)
            
            # Track directories with changes
            if comparison.left_only or comparison.right_only or comparison.diff_files:
                if rel_path:  # Don't include root directory
                    self.results['changed_dirs'].append(rel_path)
            
            # Recurse into common subdirectories
            for sub_dir in comparison.common_dirs:
                sub_rel_path = os.path.join(rel_path, sub_dir) if rel_path else sub_dir
                _compare(d1 / sub_dir, d2 / sub_dir, sub_rel_path)
        
        _compare(self.dir1, self.dir2)
        
        # Generate summary
        self.results['summary'] = {
            'comparison_time': self.comparison_time.isoformat(),
            'dir1': str(self.dir1),
            'dir2': str(self.dir2),
            'total_left_only': len(self.results['left_only']),
            'total_right_only': len(self.results['right_only']),
            'total_different': len(self.results['diff_files']),
            'total_same': len(self.results['same_files']),
            'total_changed_dirs': len(self.results['changed_dirs']),
            'has_differences': bool(self.results['left_only'] or self.results['right_only'] or self.results['diff_files'])
        }
        
        return self.results
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if a file is likely a text file."""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' not in chunk
        except IOError:
            return False

class ReportGenerator:
    """Generate various report formats from directory comparison results."""
    
    def __init__(self, results: Dict):
        self.results = results
    
    def generate_console_report(self, show_details: bool = False) -> str:
        """Generate a formatted console report."""
        report = []
        summary = self.results['summary']
        
        report.append("=" * 80)
        report.append("  DIRECTORY COMPARISON REPORT")
        report.append("=" * 80)
        report.append(f"Comparison Time: {summary['comparison_time']}")
        report.append(f"Left Directory:  {summary['dir1']}")
        report.append(f"Right Directory: {summary['dir2']}")
        report.append("")
        
        # Summary statistics
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"Files only in left:     {summary['total_left_only']}")
        report.append(f"Files only in right:    {summary['total_right_only']}")
        report.append(f"Different files:        {summary['total_different']}")
        report.append(f"Identical files:        {summary['total_same']}")
        report.append(f"Changed directories:    {summary['total_changed_dirs']}")
        report.append(f"Has differences:        {'Yes' if summary['has_differences'] else 'No'}")
        report.append("")
        
        # Files only in left directory
        if self.results['left_only']:
            report.append("FILES/DIRECTORIES ONLY IN LEFT")
            report.append("-" * 40)
            for item in self.results['left_only']:
                if item['type'] == 'file':
                    size_str = f" ({self._format_size(item['size'])})" if item.get('size') else ""
                    report.append(f"  📄 {item['path']}{size_str}")
                else:
                    report.append(f"  📁 {item['path']}/")
            report.append("")
        
        # Files only in right directory
        if self.results['right_only']:
            report.append("FILES/DIRECTORIES ONLY IN RIGHT")
            report.append("-" * 40)
            for item in self.results['right_only']:
                if item['type'] == 'file':
                    size_str = f" ({self._format_size(item['size'])})" if item.get('size') else ""
                    report.append(f"  📄 {item['path']}{size_str}")
                else:
                    report.append(f"  📁 {item['path']}/")
            report.append("")
        
        # Different files
        if self.results['diff_files']:
            report.append("DIFFERENT FILES")
            report.append("-" * 40)
            for item in self.results['diff_files']:
                left_size = self._format_size(item['left_size'])
                right_size = self._format_size(item['right_size'])
                report.append(f"  📝 {item['path']}")
                report.append(f"     Left:  {left_size} | Right: {right_size}")
                
                if show_details and item['path'] in self.results['file_details']:
                    details = self.results['file_details'][item['path']]
                    if 'lines_added' in details and 'lines_removed' in details:
                        report.append(f"     Changes: +{details['lines_added']} -{details['lines_removed']} lines")
            report.append("")
        
        # Changed directories
        if self.results['changed_dirs']:
            report.append("DIRECTORIES WITH CHANGES")
            report.append("-" * 40)
            for directory in self.results['changed_dirs']:
                report.append(f"  📁 {directory}/")
            report.append("")
        
        if show_details and self.results['file_details']:
            report.append("DETAILED FILE DIFFERENCES")
            report.append("-" * 40)
            for file_path, details in self.results['file_details'].items():
                report.append(f"\n📝 {file_path}")
                report.append("-" * len(file_path))
                if 'diff' in details:
                    for line in details['diff'][:50]:  # Limit to first 50 lines
                        report.append(line)
                    if len(details['diff']) > 50:
                        report.append(f"... ({len(details['diff']) - 50} more lines)")
                report.append("")
        
        return "\n".join(report)
    
    def generate_html_report(self) -> str:
        """Generate an HTML report."""
        summary = self.results['summary']
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Directory Comparison Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }}
        .header {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #495057; border-bottom: 2px solid #dee2e6; padding-bottom: 5px; }}
        .file-list {{ list-style: none; padding: 0; }}
        .file-item {{ padding: 8px; margin: 5px 0; border-left: 4px solid #007bff; background: #f8f9fa; }}
        .file-item.left-only {{ border-left-color: #dc3545; }}
        .file-item.right-only {{ border-left-color: #28a745; }}
        .file-item.different {{ border-left-color: #ffc107; }}
        .diff-container {{ background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; }}
        .diff-line {{ margin: 2px 0; }}
        .diff-add {{ background: #d4edda; color: #155724; }}
        .diff-remove {{ background: #f8d7da; color: #721c24; }}
        .stats {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .stat-box {{ background: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Directory Comparison Report</h1>
        <p><strong>Generated:</strong> {summary['comparison_time']}</p>
        <p><strong>Left Directory:</strong> <code>{summary['dir1']}</code></p>
        <p><strong>Right Directory:</strong> <code>{summary['dir2']}</code></p>
    </div>
    
    <div class="summary">
        <h2>📈 Summary Statistics</h2>
        <div class="stats">
            <div class="stat-box">
                <h3>🔴 Left Only</h3>
                <p style="font-size: 24px; margin: 0;">{summary['total_left_only']}</p>
            </div>
            <div class="stat-box">
                <h3>🟢 Right Only</h3>
                <p style="font-size: 24px; margin: 0;">{summary['total_right_only']}</p>
            </div>
            <div class="stat-box">
                <h3>🟡 Different</h3>
                <p style="font-size: 24px; margin: 0;">{summary['total_different']}</p>
            </div>
            <div class="stat-box">
                <h3>✅ Identical</h3>
                <p style="font-size: 24px; margin: 0;">{summary['total_same']}</p>
            </div>
        </div>
    </div>
"""
        
        # Files only in left
        if self.results['left_only']:
            html += """
    <div class="section">
        <h2>🔴 Files/Directories Only in Left</h2>
        <ul class="file-list">
"""
            for item in self.results['left_only']:
                icon = "📄" if item['type'] == 'file' else "📁"
                size_str = f" ({self._format_size(item['size'])})" if item.get('size') else ""
                html += f'            <li class="file-item left-only">{icon} {item["path"]}{size_str}</li>\n'
            html += "        </ul>\n    </div>\n"
        
        # Files only in right
        if self.results['right_only']:
            html += """
    <div class="section">
        <h2>🟢 Files/Directories Only in Right</h2>
        <ul class="file-list">
"""
            for item in self.results['right_only']:
                icon = "📄" if item['type'] == 'file' else "📁"
                size_str = f" ({self._format_size(item['size'])})" if item.get('size') else ""
                html += f'            <li class="file-item right-only">{icon} {item["path"]}{size_str}</li>\n'
            html += "        </ul>\n    </div>\n"
        
        # Different files
        if self.results['diff_files']:
            html += """
    <div class="section">
        <h2>🟡 Different Files</h2>
        <ul class="file-list">
"""
            for item in self.results['diff_files']:
                left_size = self._format_size(item['left_size'])
                right_size = self._format_size(item['right_size'])
                html += f'            <li class="file-item different">📝 {item["path"]}<br>'
                html += f'                <small>Left: {left_size} | Right: {right_size}</small></li>\n'
            html += "        </ul>\n    </div>\n"
        
        html += """
</body>
</html>
"""
        return html
    
    def generate_markdown_report(self) -> str:
        """Generate a Markdown report."""
        summary = self.results['summary']
        
        md = f"""# 📊 Directory Comparison Report

**Generated:** {summary['comparison_time']}  
**Left Directory:** `{summary['dir1']}`  
**Right Directory:** `{summary['dir2']}`

## 📈 Summary

| Metric | Count |
|--------|-------|
| Files only in left | {summary['total_left_only']} |
| Files only in right | {summary['total_right_only']} |
| Different files | {summary['total_different']} |
| Identical files | {summary['total_same']} |
| Changed directories | {summary['total_changed_dirs']} |
| Has differences | {'Yes' if summary['has_differences'] else 'No'} |

"""
        
        if self.results['left_only']:
            md += "## 🔴 Files/Directories Only in Left\n\n"
            for item in self.results['left_only']:
                icon = "📄" if item['type'] == 'file' else "📁"
                size_str = f" ({self._format_size(item['size'])})" if item.get('size') else ""
                md += f"- {icon} `{item['path']}`{size_str}\n"
            md += "\n"
        
        if self.results['right_only']:
            md += "## 🟢 Files/Directories Only in Right\n\n"
            for item in self.results['right_only']:
                icon = "📄" if item['type'] == 'file' else "📁"
                size_str = f" ({self._format_size(item['size'])})" if item.get('size') else ""
                md += f"- {icon} `{item['path']}`{size_str}\n"
            md += "\n"
        
        if self.results['diff_files']:
            md += "## 🟡 Different Files\n\n"
            for item in self.results['diff_files']:
                left_size = self._format_size(item['left_size'])
                right_size = self._format_size(item['right_size'])
                md += f"- 📝 `{item['path']}`\n"
                md += f"  - Left: {left_size} | Right: {right_size}\n"
            md += "\n"
        
        if self.results['changed_dirs']:
            md += "## 📁 Changed Directories\n\n"
            for directory in self.results['changed_dirs']:
                md += f"- 📁 `{directory}/`\n"
            md += "\n"
        
        return md
    
    def generate_json_report(self) -> str:
        """Generate a JSON report."""
        return json.dumps(self.results, indent=2, default=str)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Directory Comparison Tool with Multiple Report Formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic comparison with console output
  python diffgenerator.py dir1 dir2
  
  # Generate HTML report
  python diffgenerator.py dir1 dir2 --format html --output report.html
  
  # Generate detailed console report
  python diffgenerator.py dir1 dir2 --details
  
  # Generate JSON report for automation
  python diffgenerator.py dir1 dir2 --format json --output results.json
        """
    )
    
    parser.add_argument('dir1', help='First directory to compare')
    parser.add_argument('dir2', help='Second directory to compare')
    parser.add_argument(
        '--format', 
        choices=['console', 'html', 'markdown', 'json'],
        default='console',
        help='Output format (default: console)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file (default: stdout for console, auto-generated for others)'
    )
    parser.add_argument(
        '--details', '-d',
        action='store_true',
        help='Show detailed file differences (console format only)'
    )
    
    args = parser.parse_args()
    
    # Validate directories
    if not os.path.isdir(args.dir1):
        print(f"Error: '{args.dir1}' is not a valid directory.")
        return 1
    
    if not os.path.isdir(args.dir2):
        print(f"Error: '{args.dir2}' is not a valid directory.")
        return 1
    
    # Perform comparison
    print("Comparing directories...")
    comparator = DirectoryComparator(args.dir1, args.dir2)
    results = comparator.compare_directories()
    
    # Generate report
    generator = ReportGenerator(results)
    
    if args.format == 'console':
        report = generator.generate_console_report(show_details=args.details)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Console report saved to: {args.output}")
        else:
            print(report)
    
    elif args.format == 'html':
        report = generator.generate_html_report()
        output_file = args.output or f"diff_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"HTML report saved to: {output_file}")
    
    elif args.format == 'markdown':
        report = generator.generate_markdown_report()
        output_file = args.output or f"diff_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Markdown report saved to: {output_file}")
    
    elif args.format == 'json':
        report = generator.generate_json_report()
        output_file = args.output or f"diff_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"JSON report saved to: {output_file}")
    
    # Return exit code based on whether differences were found
    return 0 if not results['summary']['has_differences'] else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
