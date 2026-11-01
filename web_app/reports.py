from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

def generate_movies_report(movies, filename='movies_report.pdf'):
    """
    Генерація PDF-звіту зі списком фільмів
    """
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Заголовок звіту
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1  # Центрування
    )

    title = Paragraph("Звіт про каталог фільмів", title_style)
    elements.append(title)

    # Дата генерації
    date_text = Paragraph(
        f"Дата формування: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        styles['Normal']
    )
    elements.append(date_text)
    elements.append(Spacer(1, 20))

    # Таблиця з даними (ID, Назва, Рік, Тривалість, Рейтинг, Бюджет)
    data = [['№', 'Назва фільму', 'Рік', 'Хв.', 'Рейтинг', 'Бюджет ($)']]

    for idx, movie in enumerate(movies, 1):
        budget_str = f"{movie[5]:,.2f}" if movie[5] is not None else "0.00"
        data.append([
            str(idx),
            str(movie[1])[:35],  # Обмеження довжини назви
            str(movie[2]),
            str(movie[3]),
            str(movie[4]),
            budget_str
        ])

    # Створення таблиці
    table = Table(data, colWidths=[0.5*inch, 3.2*inch, 0.8*inch, 0.8*inch, 1*inch, 1.4*inch])

    # Стилізація таблиці
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#f8f9fa')])
    ]))

    elements.append(table)

    # Статистика
    elements.append(Spacer(1, 20))
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

    stats = Paragraph(stats_text, styles['Normal'])
    elements.append(stats)

    # Генерація PDF
    doc.build(elements)
    return filename