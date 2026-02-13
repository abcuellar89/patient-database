#!/usr/bin/env python3
"""
Patient Database Application - Dr. Adrian Cuellar
A simple local web application to view and search patient data from Google Sheets.

Usage:
1. Install dependencies: pip install flask requests
2. Run: python patient_database.py
3. Open http://localhost:5000 in your browser
"""

import csv
import io
import webbrowser
from datetime import datetime
from flask import Flask, render_template_string, jsonify, request
import requests

app = Flask(__name__)

# Configuration
GOOGLE_SHEET_ID = "1JZN0aAlnVZEXXqeNF3JnbotWf0Az59Iwtv0wtJ6OmKE"
GID = "571971247"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=csv&gid={GID}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Base de Datos de Pacientes - Dr. Adrian Cuellar</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #1a3a5c;
            --primary-light: #2d5a8b;
            --accent: #e8a838;
            --bg: #f8f9fa;
            --card-bg: #ffffff;
            --text: #1a1a1a;
            --text-muted: #6c757d;
            --border: #e0e4e8;
            --success: #28a745;
            --row-hover: #f0f7ff;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            line-height: 1.6;
        }

        .header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
            color: white;
            padding: 2rem 3rem;
            box-shadow: 0 4px 20px rgba(26, 58, 92, 0.15);
        }

        .header-content { max-width: 1600px; margin: 0 auto; }

        .header h1 {
            font-family: 'Playfair Display', serif;
            font-size: 1.8rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
        }

        .header p { opacity: 0.85; font-size: 0.9rem; }

        .controls {
            max-width: 1600px;
            margin: 0 auto;
            padding: 1.5rem 3rem;
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }

        .search-container {
            flex: 1;
            min-width: 300px;
            position: relative;
        }

        .search-container::before {
            content: "🔍";
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            opacity: 0.5;
        }

        .search-input {
            width: 100%;
            padding: 0.875rem 1rem 0.875rem 2.75rem;
            border: 2px solid var(--border);
            border-radius: 12px;
            font-size: 0.95rem;
            font-family: inherit;
            transition: all 0.2s ease;
            background: var(--card-bg);
        }

        .search-input:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 4px rgba(26, 58, 92, 0.1);
        }

        .stats {
            display: flex;
            gap: 1.5rem;
            font-size: 0.85rem;
            color: var(--text-muted);
        }

        .stat-item { display: flex; align-items: center; gap: 0.5rem; }

        .stat-value {
            font-weight: 600;
            color: var(--primary);
            font-size: 1.1rem;
        }

        .refresh-btn {
            padding: 0.75rem 1.25rem;
            background: var(--card-bg);
            border: 2px solid var(--border);
            border-radius: 10px;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .refresh-btn:hover {
            border-color: var(--primary);
            background: var(--row-hover);
        }

        .main-content {
            max-width: 1600px;
            margin: 0 auto;
            padding: 0 3rem 3rem;
        }

        .table-container {
            background: var(--card-bg);
            border-radius: 16px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
            overflow: hidden;
        }

        .table-wrapper {
            overflow-x: auto;
            max-height: calc(100vh - 280px);
            overflow-y: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
        }

        thead { position: sticky; top: 0; z-index: 10; }

        th {
            background: var(--primary);
            color: white;
            padding: 1rem 0.75rem;
            text-align: left;
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
            cursor: pointer;
            transition: background 0.2s ease;
        }

        th:hover { background: var(--primary-light); }
        th.sorted-asc::after { content: " ↑"; }
        th.sorted-desc::after { content: " ↓"; }

        td {
            padding: 0.875rem 0.75rem;
            border-bottom: 1px solid var(--border);
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        td:first-child { font-weight: 500; color: var(--primary); }
        tr:hover td { background: var(--row-hover); }

        .copy-btn {
            padding: 0.5rem 1rem;
            background: linear-gradient(135deg, var(--accent) 0%, #d4922c 100%);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.8rem;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(232, 168, 56, 0.3);
        }

        .copy-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(232, 168, 56, 0.4);
        }

        .copy-btn.copied {
            background: var(--success);
        }

        .loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 4rem;
        }

        .spinner {
            width: 48px;
            height: 48px;
            border: 4px solid var(--border);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1rem;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        .error-message {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem;
            color: #856404;
        }

        .no-results {
            text-align: center;
            padding: 3rem;
            color: var(--text-muted);
        }

        .toast {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            background: var(--primary);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 1000;
        }

        .toast.show { transform: translateY(0); opacity: 1; }

        @media (max-width: 768px) {
            .header, .controls, .main-content { padding-left: 1rem; padding-right: 1rem; }
            .controls { flex-direction: column; }
            .search-container { min-width: 100%; }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <h1>🏥 Base de Datos de Pacientes</h1>
            <p>Dr. Adrian Cuellar - Cuestionario de Consulta</p>
        </div>
    </header>

    <div class="controls">
        <div class="search-container">
            <input type="text" class="search-input" id="searchInput" placeholder="Buscar por nombre, apellido, fecha, o cualquier campo...">
        </div>
        <div class="stats">
            <div class="stat-item">
                <span>Total:</span>
                <span class="stat-value" id="totalCount">-</span>
            </div>
            <div class="stat-item">
                <span>Mostrando:</span>
                <span class="stat-value" id="filteredCount">-</span>
            </div>
        </div>
        <button class="refresh-btn" onclick="loadData()">🔄 Actualizar</button>
    </div>

    <main class="main-content">
        <div class="table-container">
            <div id="loadingOverlay" class="loading">
                <div class="spinner"></div>
                <p>Cargando datos...</p>
            </div>
            <div id="errorContainer"></div>
            <div class="table-wrapper" id="tableWrapper" style="display: none;">
                <table id="dataTable">
                    <thead id="tableHead"></thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
            <div id="noResults" class="no-results" style="display: none;">
                <h3>No se encontraron resultados</h3>
                <p>Intenta con otros términos de búsqueda</p>
            </div>
        </div>
    </main>

    <div class="toast" id="toast"></div>

    <script>
        let allData = [];
        let filteredData = [];
        let headers = [];
        let sortColumn = 0;
        let sortDirection = 'desc';

        async function loadData() {
            document.getElementById('loadingOverlay').style.display = 'flex';
            document.getElementById('tableWrapper').style.display = 'none';
            document.getElementById('errorContainer').innerHTML = '';

            try {
                const response = await fetch('/api/data');
                const result = await response.json();
                
                if (result.error) throw new Error(result.error);
                
                headers = result.headers;
                allData = result.data;
                filteredData = [...allData];
                
                sortColumn = 0;
                sortDirection = 'desc';
                sortData();
                renderTable();
                updateStats();
                
                document.getElementById('loadingOverlay').style.display = 'none';
                document.getElementById('tableWrapper').style.display = 'block';
            } catch (error) {
                document.getElementById('loadingOverlay').style.display = 'none';
                document.getElementById('errorContainer').innerHTML = `
                    <div class="error-message">
                        <h3>⚠️ Error al cargar los datos</h3>
                        <p>${error.message}</p>
                        <p>Asegúrate de que el Google Sheet esté compartido con "Cualquier persona con el enlace".</p>
                    </div>
                `;
            }
        }

        function sortData() {
            const data = document.getElementById('searchInput').value ? filteredData : allData;
            data.sort((a, b) => {
                let valA = a[sortColumn] || '';
                let valB = b[sortColumn] || '';
                
                if (sortColumn === 0) {
                    const dateA = new Date(valA);
                    const dateB = new Date(valB);
                    if (!isNaN(dateA) && !isNaN(dateB)) {
                        return sortDirection === 'asc' ? dateA - dateB : dateB - dateA;
                    }
                }
                
                return sortDirection === 'asc' 
                    ? valA.localeCompare(valB, 'es') 
                    : valB.localeCompare(valA, 'es');
            });
        }

        function handleSort(colIndex) {
            if (sortColumn === colIndex) {
                sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                sortColumn = colIndex;
                sortDirection = 'asc';
            }
            sortData();
            renderTable();
        }

        function filterData(searchTerm) {
            const term = searchTerm.toLowerCase().trim();
            filteredData = term 
                ? allData.filter(row => row.some(cell => cell.toLowerCase().includes(term)))
                : [...allData];
            sortData();
            renderTable();
            updateStats();
        }

        function truncate(text, max) {
            if (!text) return '';
            return text.length > max ? text.substring(0, max) + '...' : text;
        }

        function escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function renderTable() {
            const data = document.getElementById('searchInput').value ? filteredData : allData;
            
            document.getElementById('tableHead').innerHTML = `
                <tr>
                    ${headers.map((h, i) => `
                        <th onclick="handleSort(${i})" class="${sortColumn === i ? 'sorted-' + sortDirection : ''}">
                            ${truncate(h, 30)}
                        </th>
                    `).join('')}
                    <th style="cursor: default;">Acciones</th>
                </tr>
            `;

            if (data.length === 0) {
                document.getElementById('tableBody').innerHTML = '';
                document.getElementById('noResults').style.display = 'block';
                return;
            }
            
            document.getElementById('noResults').style.display = 'none';
            
            document.getElementById('tableBody').innerHTML = data.map((row, i) => `
                <tr>
                    ${row.map(cell => `<td title="${escapeHtml(cell)}">${truncate(escapeHtml(cell), 40)}</td>`).join('')}
                    ${row.length < headers.length ? Array(headers.length - row.length).fill('<td></td>').join('') : ''}
                    <td><button class="copy-btn" onclick="copyPatientInfo(${i})">📋 Copiar como texto</button></td>
                </tr>
            `).join('');
        }

        function updateStats() {
            document.getElementById('totalCount').textContent = allData.length;
            document.getElementById('filteredCount').textContent = 
                document.getElementById('searchInput').value ? filteredData.length : allData.length;
        }

        function copyPatientInfo(rowIndex) {
            const data = document.getElementById('searchInput').value ? filteredData : allData;
            const row = data[rowIndex];
            
            let text = '';
            headers.forEach((header, i) => {
                const value = row[i] || '';
                if (value.trim()) {
                    text += `-*${header.toUpperCase()}*:   ${value}\\n`;
                }
            });
            
            navigator.clipboard.writeText(text.trim()).then(() => {
                showToast('✓ Información copiada al portapapeles');
                const btn = event.target;
                btn.textContent = '✓ Copiado';
                btn.classList.add('copied');
                setTimeout(() => {
                    btn.innerHTML = '📋 Copiar como texto';
                    btn.classList.remove('copied');
                }, 2000);
            });
        }

        function showToast(message) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }

        document.getElementById('searchInput').addEventListener('input', e => filterData(e.target.value));
        
        document.addEventListener('keydown', e => {
            if (e.key === '/' && e.target.tagName !== 'INPUT') {
                e.preventDefault();
                document.getElementById('searchInput').focus();
            }
            if (e.key === 'Escape') {
                document.getElementById('searchInput').value = '';
                filterData('');
            }
        });

        loadData();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    try:
        response = requests.get(SHEET_URL, timeout=30)
        response.raise_for_status()
        
        # Parse CSV
        content = response.content.decode('utf-8')
        reader = csv.reader(io.StringIO(content))
        rows = list(reader)
        
        if len(rows) < 2:
            return jsonify({'error': 'No hay datos suficientes'})
        
        headers = rows[0]
        data = [row for row in rows[1:] if any(cell.strip() for cell in row)]
        
        return jsonify({
            'headers': headers,
            'data': data
        })
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Error de conexión: {str(e)}'})
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'})

if __name__ == '__main__':
    print("=" * 50)
    print("🏥 Base de Datos de Pacientes")
    print("   Dr. Adrian Cuellar")
    print("=" * 50)
    print()
    print("Abriendo navegador en: http://localhost:5000")
    print("Presiona Ctrl+C para detener el servidor")
    print()
    
    # Open browser automatically
    webbrowser.open('http://localhost:5000')
    
    # Run Flask app
    app.run(debug=False, port=5000)
