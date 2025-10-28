"""
Visual PDF Test Script
Generates an HTML report with complete extracted data from all PDFs
"""
import os
import glob
import json
from datetime import datetime
from pathlib import Path
from pdf_extract import parse_pdf_to_records

def read_expected_data():
    """Read the expected data from the text file for comparison"""
    txt_path = "../dummyinfo/Text die geëxtraheerd moet worden uit de PDF.txt"
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read expected data: {e}")
        return None

def parse_expected_data(text):
    """Parse expected data into structured format for comparison"""
    if not text:
        return None
    
    lines = text.strip().split('\n')
    expected = {
        'metadata': {},
        'rows': [],
        'totals': None
    }
    
    # Parse metadata from first lines
    for line in lines[:20]:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if key and value:
                expected['metadata'][key] = value
    
    # Find table start (line with maat labels)
    table_start = None
    for i, line in enumerate(lines):
        if 'XXS' in line and 'XS' in line and 'Verkocht' in line:
            table_start = i
            break
    
    if table_start:
        # Parse data rows
        for line in lines[table_start + 1:]:
            line = line.strip()
            if not line or line.startswith('---'):
                continue
            
            parts = line.split('\t')
            if len(parts) > 3:
                expected['rows'].append({
                    'raw_line': line,
                    'parts': parts
                })
    
    return expected

def generate_html_report(results, expected_data=None):
    """Generate comprehensive HTML report with all extracted data"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Count statuses
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    partial_count = sum(1 for r in results if r['status'] == 'PARTIAL_SUCCESS')
    failed_count = sum(1 for r in results if r['status'] == 'FAILED')
    exception_count = sum(1 for r in results if r['status'] == 'EXCEPTION')
    
    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Extraction Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .header .timestamp {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            color: white;
        }}
        
        .stat-card.success {{ background: #10b981; }}
        .stat-card.partial {{ background: #f59e0b; }}
        .stat-card.failed {{ background: #ef4444; }}
        .stat-card.exception {{ background: #dc2626; }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .overview-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 40px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .overview-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .overview-table td {{
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .overview-table tr:hover {{
            background: #f9fafb;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .status-badge.success {{ background: #d1fae5; color: #065f46; }}
        .status-badge.partial {{ background: #fef3c7; color: #92400e; }}
        .status-badge.failed {{ background: #fee2e2; color: #991b1b; }}
        .status-badge.exception {{ background: #fecaca; color: #7f1d1d; }}
        
        .pdf-detail {{
            margin-bottom: 50px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .pdf-header {{
            background: #f9fafb;
            padding: 20px;
            border-bottom: 2px solid #e5e7eb;
        }}
        
        .pdf-header h2 {{
            color: #1f2937;
            margin-bottom: 5px;
        }}
        
        .pdf-content {{
            padding: 20px;
        }}
        
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        
        .metadata-item {{
            background: #f9fafb;
            padding: 12px;
            border-radius: 6px;
            border-left: 3px solid #667eea;
        }}
        
        .metadata-item .label {{
            font-weight: 600;
            color: #4b5563;
            font-size: 0.85em;
            margin-bottom: 3px;
        }}
        
        .metadata-item .value {{
            color: #1f2937;
            font-size: 1em;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 0.9em;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .data-table th {{
            background: #374151;
            color: white;
            padding: 10px 8px;
            text-align: center;
            font-weight: 600;
            font-size: 0.85em;
            border: 1px solid #1f2937;
        }}
        
        .data-table td {{
            padding: 8px;
            border: 1px solid #e5e7eb;
            text-align: center;
        }}
        
        .data-table tbody tr:nth-child(even) {{
            background: #f9fafb;
        }}
        
        .data-table tbody tr:hover {{
            background: #f3f4f6;
        }}
        
        .data-table .filiaal-cell {{
            text-align: left;
            font-weight: 500;
        }}
        
        .data-table .totals-row {{
            background: #dbeafe !important;
            font-weight: 600;
        }}
        
        .data-table .totals-row td {{
            border-top: 2px solid #374151;
        }}
        
        .empty-value {{
            color: #9ca3af;
        }}
        
        .warning-box {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .warning-box h4 {{
            color: #92400e;
            margin-bottom: 10px;
        }}
        
        .warning-box ul {{
            margin-left: 20px;
            color: #78350f;
        }}
        
        .error-box {{
            background: #fee2e2;
            border-left: 4px solid #ef4444;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        
        .error-box h4 {{
            color: #991b1b;
            margin-bottom: 10px;
        }}
        
        .error-box ul {{
            margin-left: 20px;
            color: #7f1d1d;
        }}
        
        .comparison-section {{
            margin-top: 30px;
            padding: 20px;
            background: #f0fdf4;
            border: 2px solid #10b981;
            border-radius: 8px;
        }}
        
        .comparison-section h3 {{
            color: #065f46;
            margin-bottom: 15px;
        }}
        
        .size-badge {{
            display: inline-block;
            background: #e0e7ff;
            color: #3730a3;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            margin: 2px;
            font-weight: 500;
        }}
        
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 PDF Extraction Test Report</h1>
            <div class="timestamp">Generated: {timestamp}</div>
        </div>
        
        <div class="summary">
            <div class="stat-card success">
                <div class="number">{success_count}</div>
                <div class="label">✓ Succesvol</div>
            </div>
            <div class="stat-card partial">
                <div class="number">{partial_count}</div>
                <div class="label">⚠️ Gedeeltelijk</div>
            </div>
            <div class="stat-card failed">
                <div class="number">{failed_count}</div>
                <div class="label">✗ Mislukt</div>
            </div>
            <div class="stat-card exception">
                <div class="number">{exception_count}</div>
                <div class="label">💥 Exception</div>
            </div>
        </div>
        
        <h2 style="margin-bottom: 15px;">📋 Overzicht</h2>
        <table class="overview-table">
            <thead>
                <tr>
                    <th>Bestand</th>
                    <th>Status</th>
                    <th>Volgnummer</th>
                    <th>Rijen</th>
                    <th>Maten</th>
                    <th>Errors</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add overview rows
    for r in results:
        status_class = r['status'].lower().replace('_', '-')
        status_icon = {
            'SUCCESS': '✓',
            'PARTIAL_SUCCESS': '⚠️',
            'FAILED': '✗',
            'EXCEPTION': '💥'
        }.get(r['status'], '?')
        
        html += f"""
                <tr>
                    <td><strong>{r['filename']}</strong></td>
                    <td><span class="status-badge {status_class}">{status_icon} {r['status']}</span></td>
                    <td>{r.get('volgnummer', 'N/A')}</td>
                    <td>{r.get('row_count', 0)}</td>
                    <td>{len(r.get('sizes', []))} maten</td>
                    <td>{r.get('error_count', 0)}</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        
        <h2 style="margin: 40px 0 20px 0;">📄 Gedetailleerde Extractie Data</h2>
"""
    
    # Add detailed section for each PDF
    for r in results:
        status_class = r['status'].lower().replace('_', '-')
        status_icon = {
            'SUCCESS': '✓',
            'PARTIAL_SUCCESS': '⚠️',
            'FAILED': '✗',
            'EXCEPTION': '💥'
        }.get(r['status'], '?')
        
        html += f"""
        <div class="pdf-detail">
            <div class="pdf-header">
                <h2>📄 {r['filename']}</h2>
                <span class="status-badge {status_class}">{status_icon} {r['status']}</span>
            </div>
            <div class="pdf-content">
"""
        
        # Exception handling
        if r['status'] == 'EXCEPTION':
            html += f"""
                <div class="error-box">
                    <h4>💥 Exception tijdens verwerking</h4>
                    <p>{r.get('error', 'Onbekende fout')}</p>
                </div>
"""
        else:
            # Metadata
            if r.get('metadata'):
                html += """
                <h3>📋 Metadata</h3>
                <div class="metadata-grid">
"""
                for key, value in r['metadata'].items():
                    html += f"""
                    <div class="metadata-item">
                        <div class="label">{key}</div>
                        <div class="value">{value}</div>
                    </div>
"""
                html += """
                </div>
"""
            
            # Sizes detected
            if r.get('sizes'):
                html += """
                <h3>📏 Gedetecteerde Maten</h3>
                <p style="margin: 10px 0;">
"""
                for size in r['sizes']:
                    html += f'<span class="size-badge">{size}</span>'
                html += """
                </p>
"""
            
            # Data table
            if r.get('rows'):
                sizes = r.get('sizes', [])
                html += f"""
                <h3>📊 Voorraad Data ({len(r['rows'])} rijen)</h3>
                <div style="overflow-x: auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Code</th>
                                <th>Filiaal</th>
"""
                # Add size columns
                for size in sizes:
                    html += f"<th>{size}</th>"
                
                html += """
                                <th>Verkocht</th>
                            </tr>
                        </thead>
                        <tbody>
"""
                
                # Add data rows
                for row in r['rows']:
                    html += f"""
                            <tr>
                                <td>{row.get('filiaal_code', '')}</td>
                                <td class="filiaal-cell">{row.get('filiaal_naam', '')}</td>
"""
                    voorraad = row.get('voorraad_per_maat', {})
                    for size in sizes:
                        value = voorraad.get(size, 0)
                        if value == 0:
                            html += '<td class="empty-value">.</td>'
                        else:
                            html += f'<td><strong>{value}</strong></td>'
                    
                    verkocht = row.get('verkocht', 0)
                    html += f'<td>{verkocht if verkocht > 0 else "."}</td>'
                    html += """
                            </tr>
"""
                
                # Add totals row if available
                if r.get('totals'):
                    totals = r['totals']
                    html += """
                            <tr class="totals-row">
                                <td></td>
                                <td class="filiaal-cell">TOTAAL</td>
"""
                    totals_voorraad = totals.get('voorraad_per_maat', {})
                    for size in sizes:
                        value = totals_voorraad.get(size, 0)
                        if value == 0:
                            html += '<td class="empty-value">.</td>'
                        else:
                            html += f'<td><strong>{value}</strong></td>'
                    
                    totals_verkocht = totals.get('verkocht', 0)
                    html += f'<td><strong>{totals_verkocht}</strong></td>'
                    html += """
                            </tr>
"""
                
                html += """
                        </tbody>
                    </table>
                </div>
"""
            
            # Warnings
            if r.get('warnings'):
                html += """
                <div class="warning-box">
                    <h4>⚠️ Waarschuwingen</h4>
                    <ul>
"""
                for warning in r['warnings']:
                    html += f"<li>{warning}</li>"
                html += """
                    </ul>
                </div>
"""
            
            # Errors
            if r.get('errors'):
                html += """
                <div class="error-box">
                    <h4>✗ Errors</h4>
                    <ul>
"""
                for error in r['errors']:
                    html += f"<li>{error}</li>"
                html += """
                    </ul>
                </div>
"""
            
            # Negative voorraad detection
            if r.get('negative_voorraad'):
                html += """
                <div class="warning-box">
                    <h4>⚠️ Negatieve Voorraad Gedetecteerd</h4>
                    <ul>
"""
                for neg in r['negative_voorraad']:
                    html += f"""<li>Filiaal {neg['filiaal_code']} ({neg['filiaal_naam']}), 
                               Maat {neg['maat']}: {neg['raw_value']} → 0</li>"""
                html += """
                    </ul>
                </div>
"""
        
        html += """
            </div>
        </div>
"""
    
    # Add comparison section for 423264 if available
    if expected_data:
        html += """
        <div class="comparison-section">
            <h3>🔍 Vergelijking met Verwachte Data (423264.pdf)</h3>
            <p>De verwachte data is beschikbaar in: <code>Text die geëxtraheerd moet worden uit de PDF.txt</code></p>
            <p><em>Handmatige verificatie aanbevolen door beide documenten naast elkaar te bekijken.</em></p>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    return html

def test_all_pdfs_visual():
    """Test all PDFs and generate visual HTML report"""
    
    print("=" * 100)
    print("📊 VISUAL PDF EXTRACTION TEST")
    print("=" * 100)
    
    # Find all PDFs
    pdf_folder = "../dummyinfo"
    pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_folder}")
        return
    
    print(f"\nGevonden: {len(pdf_files)} PDF bestand(en)")
    print("-" * 100)
    
    results = []
    
    # Read expected data
    expected_data = read_expected_data()
    
    # Process each PDF
    for pdf_path in sorted(pdf_files):
        filename = os.path.basename(pdf_path)
        print(f"\n📄 Verwerken: {filename}")
        
        try:
            # Parse PDF
            result = parse_pdf_to_records(pdf_path)
            
            # Determine status
            if result.errors:
                if result.rows:
                    status = 'PARTIAL_SUCCESS'
                else:
                    status = 'FAILED'
            else:
                status = 'SUCCESS'
            
            # Build result dict
            result_dict = {
                'filename': filename,
                'status': status,
                'volgnummer': result.meta.get('Volgnummer', 'N/A'),
                'metadata': result.meta,
                'sizes': result.sizes,
                'rows': result.rows,
                'totals': result.totals,
                'row_count': len(result.rows),
                'error_count': len(result.errors),
                'errors': result.errors,
                'warnings': result.warnings,
                'negative_voorraad': getattr(result, 'negative_voorraad_detected', [])
            }
            
            print(f"   Status: {status}")
            print(f"   Rijen: {len(result.rows)}")
            print(f"   Maten: {len(result.sizes)}")
            
            results.append(result_dict)
            
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            results.append({
                'filename': filename,
                'status': 'EXCEPTION',
                'error': str(e)
            })
    
    print("\n" + "=" * 100)
    print("📝 Genereren HTML rapport...")
    
    # Generate HTML report
    html_content = generate_html_report(results, expected_data)
    
    # Save HTML report
    output_path = "pdf_extraction_report.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ HTML rapport opgeslagen: {output_path}")
    
    # Generate JSON export
    json_output_path = "pdf_extraction_data.json"
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✓ JSON data opgeslagen: {json_output_path}")
    
    # Summary
    print("\n" + "=" * 100)
    print("📈 SAMENVATTING")
    print("=" * 100)
    
    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    partial_count = sum(1 for r in results if r['status'] == 'PARTIAL_SUCCESS')
    failed_count = sum(1 for r in results if r['status'] == 'FAILED')
    exception_count = sum(1 for r in results if r['status'] == 'EXCEPTION')
    
    print(f"\nTotaal bestanden: {len(results)}")
    print(f"  ✓ Succesvol: {success_count}")
    print(f"  ⚠️  Gedeeltelijk: {partial_count}")
    print(f"  ✗ Mislukt: {failed_count}")
    print(f"  💥 Exceptions: {exception_count}")
    
    print("\n" + "=" * 100)
    print(f"🌐 Open het rapport in je browser: {os.path.abspath(output_path)}")
    print("=" * 100)

if __name__ == "__main__":
    test_all_pdfs_visual()
