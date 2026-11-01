import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

def generate_movies_report(movies, filename='movies_report.pdf'):
    """
    Генерація PDF-звіту зі списком фільмів з підтримкою української кирилиці (Arial)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, filename)

    # Реєструємо системний шрифт Windows із підтримкою кирилиці
    font_path = "C:/Windows/Fonts/arial.ttf"
    font_bold_path = "C:/Windows/Fonts/arialbd.ttf"
    
    if os.path.exists(font_path) and os.path.exists(font_bold_path):
        pdfmetrics.registerFont(TTFont('ArialUnicode', font_path))
        pdfmetrics.registerFont(TTFont('ArialUnicode-Bold', font_bold_path))
        font_regular = 'ArialUnicode'
        font_bold = 'ArialUnicode-Bold'
    else:
        # Резервний варіант, якщо шлях відрізняється
        font_regular = 'Helvetica'
        font_bold = 'Helvetica-Bold'

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Створюємо стилі з підтримкою нашого шрифту
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=22,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=1  # Центрування
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_regular,
        fontSize=10,
        textColor=colors.HexColor('#333333')
    )

    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontName=font_bold,
        fontSize=10,
        textColor=colors.HexColor('#333333')
    )

    # Заголовок звіту
    title = Paragraph("Звіт про каталог фільмів", title_style)
    elements.append(title)

    # Дата генерації
    date_text = Paragraph(
        f"<b>Дата формування:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        normal_style
    )
    elements.append(date_text)
    elements.append(Spacer(1, 15))

    # Таблиця з даними
    data = [['№', 'Назва фільму', 'Рік', 'Хв.', 'Рейтинг', 'Бюджет ($)']]

    for idx, movie in enumerate(movies, 1):
        budget_str = f"{movie[5]:,.2f}" if movie[5] is not None else "0.00"
        data.append([
            str(idx),
            str(movie[1])[:30],
            str(movie[2]),
            str(movie[3]),
            str(movie[4]),
            budget_str
        ])

    # Загортаємо комірки таблиці у Paragraph, щоб вони коректно рендерили кастомний шрифт
    table_data = []
    for row_idx, row in enumerate(data):
        row_cells = []
        for cell in row:
            p_style = bold_style if row_idx == 0 else normal_style
            row_cells.append(Paragraph(str(cell), p_style))
        table_data.append(row_cells)

    table = Table(table_data, colWidths=[0.4*inch, 3.0*inch, 0.8*inch, 0.8*inch, 1*inch, 1.5*inch])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))

    elements.append(table)

    # Статистика
    elements.append(Spacer(1, 15))
    total_movies = len(movies)
    valid_budgets = [m[5] for m in movies if m[5] is not None]
    total_budget = sum(valid_budgets)
    avg_budget = total_budget / len(valid_budgets) if valid_budgets else 0

    stats_text = f"""
    <b>Статистика каталогу:</b><br/>
    Всього фільмів: {total_movies}<br/>
    Загальний бюджет: ${total_budget:,.2f}<br/>
    Середній бюджет: ${avg_budget:,.2f}
    """

    stats = Paragraph(stats_text, normal_style)
    elements.append(stats)

    # Генерація PDF
    doc.build(elements)
    return file_path