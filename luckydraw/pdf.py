
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import io


def generate_pdf(pdf_data, accounts_dict,date_range):
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Create a list to hold the PDF contents
    elements = []

    # Define the styles
    styles = getSampleStyleSheet()
    normal_style = styles['Heading2']
    heading_style = styles['Heading1']
    normal_style.alignment = 1  # Center alignment
    heading_style.alignment = 1  # Center alignment

    # Add a heading
    elements.append(Paragraph("Name", heading_style))

    # Add a sub-information or caption
    elements.append(Paragraph(f"{date_range[0]} to {date_range[1]}", normal_style))
    
    # Add data to a table
    data = [["Coupen number", "Count", "Prize"]]

    # extend pdf_data to data
    data.extend(pdf_data)

    table = Table(data, colWidths=100, rowHeights=30)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    elements.append(table)
    
    # Sum of winnig prizes
    total_winning_amount = accounts_dict.get("total_winning_prize")
    elements.append(Paragraph(f"Total Winning amount: {total_winning_amount}",styles['Heading3']))

    # Add a spacer
    elements.append(Spacer(1, 12))

    # Create a new table to show the calculations
    data2 = [
        ["Coupen type","Type_total"],
        ["BLOCK total",accounts_dict.get("BLOCK")],
        ["BOX total",accounts_dict.get("BOX")],
        ["Block total",accounts_dict.get("SUPER")]
    ]

    table2 = Table(data2, colWidths=100, rowHeights=30)
    table2.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))


    elements.append(table2)

    # Sum of winnig prizes
    total_sum = accounts_dict["total_sum"]
    elements.append(Paragraph(f"Total coupen rate: {total_sum}", styles['Heading3']))

    # Sum of winnig prizes
    account_balance = accounts_dict["account_balance"]
    elements.append(Paragraph(f"Account balance: {account_balance}", styles['Heading2']))

    # Build the PDF document
    doc.build(elements)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return buffer



# winners list pdf
def generate_winner_pdf(winner_list,context):
    """
    """
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Create a list to hold the PDF contents
    elements = []

    # Define the styles
    styles = getSampleStyleSheet()
    normal_style = styles['Heading2']
    heading_style = styles['Heading1']
    normal_style.alignment = 1  # Center alignment
    heading_style.alignment = 1  # Center alignment

    # Add a heading
    elements.append(Paragraph("Winners report", heading_style))

    # Add a sub-information or caption
    elements.append(Paragraph(f"{context.context_date} Contest", normal_style))
    elements.append(Paragraph(f"{context.luckydrawtype_id.luckydraw_name}", normal_style))

    
    # Add data to a table
    data = [["Coupen number", "Prize", "Count","amount"]]

    # extend pdf_data to data
    data.extend(winner_list)

    table = Table(data, colWidths=100, rowHeights=30)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    elements.append(table)

    # Build the PDF document
    doc.build(elements)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return buffer




def generate_resultreport_pdf(count_table=None,prize_table=None,reduced_winners_list=None, profit = None, date_range=None, luckydraw_instance=None):
    """
    """
    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Create a list to hold the PDF contents
    elements = []

    # Define the styles
    styles = getSampleStyleSheet()
    normal_style = styles['Heading2']
    heading_style = styles['Heading1']
    normal_style.alignment = 1  # Center alignment
    heading_style.alignment = 1  # Center alignment

    # Add a heading
    elements.append(Paragraph("Results and Reports", heading_style))

    # Add a sub-information or caption
    elements.append(Paragraph(f"{date_range[0]} to {date_range[1]}", normal_style))
    
    # lucky draw details
    elements.append(Paragraph(f"{luckydraw_instance.luckydraw_name}", normal_style))
    
    # Format as 12-hour clock with AM/PM
    normal_time = luckydraw_instance.draw_time.strftime("%I:%M %p")
    
    elements.append(Paragraph(f"Drow time: {normal_time}", normal_style))

    # Defining table
    count_table_data = [["Coupen type", "Count","Amount"]]
    prize_table_data = [["Prize", "Prize Amount"]]
    reduced_winners_data = [["Coupen Number","Prize","Count","Amount"]]

    # extend data into defined tables
    count_table_data.extend(count_table)
    prize_table_data.extend(prize_table)
    reduced_winners_data.extend(reduced_winners_list)
    
    # create count_table_data
    table1 = Table(count_table_data, colWidths=120, rowHeights=30)
    table1.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    elements.append(table1)

    # Add a spacer
    elements.append(Spacer(1, 12))

    # create prize table
    table2 = Table(prize_table_data, colWidths=120, rowHeights=30)
    table2.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    elements.append(table2)

    # show profit
    elements.append(Paragraph(f"Total Profit: {profit}", styles['Heading3']))

    # winneres table data
    table3 = Table(reduced_winners_data, colWidths=120, rowHeights=30)
    table3.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    elements.append(table3)

    # Build the PDF document
    doc.build(elements)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    return buffer
