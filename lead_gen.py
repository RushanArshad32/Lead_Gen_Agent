import streamlit as st
import anthropic
import json
from typing import Dict, List
import time
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io

# Page configuration
st.set_page_config(
    page_title="Lead Generation Agent",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

def generate_pdf_report(company_name: str, fit_data: Dict, pain_data: Dict = None) -> bytes:
    """
    Generate a professional PDF report of the lead analysis
    
    This function creates a formatted PDF document with:
    - Company overview and fit analysis
    - Pain points and solutions (if available)
    - Engagement strategy
    - Recommended next steps
    """
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    story = []
    
    # Define custom styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )
    
    # Title
    story.append(Paragraph("Lead Analysis Report", title_style))
    story.append(Paragraph(f"<b>{company_name}</b>", heading_style))
    story.append(Paragraph(f"Generated: {time.strftime('%B %d, %Y at %I:%M %p')}", normal_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Company Overview Section
    story.append(Paragraph("Company Overview", heading_style))
    story.append(Paragraph(fit_data['brief_company_overview'], normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Fit Analysis Section
    story.append(Paragraph("Fit Analysis", heading_style))
    
    # Create fit metrics table
    fit_data_table = [
        ['Metric', 'Value'],
        ['Industry', fit_data['industry']],
        ['Sector', fit_data['sector']],
        ['Company Size', fit_data['company_size']],
        ['Fit Score', f"{fit_data['fit_score']}/100"],
        ['Good Fit?', 'Yes ✓' if fit_data['is_good_fit'] else 'No ✗']
    ]
    
    fit_table = Table(fit_data_table, colWidths=[2*inch, 4*inch])
    fit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(fit_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("Fit Assessment Reasoning", subheading_style))
    story.append(Paragraph(fit_data['fit_reasoning'], normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Pain Points and Solutions (if available)
    if pain_data:
        story.append(PageBreak())
        story.append(Paragraph("Pain Points Analysis", heading_style))
        
        for idx, pain in enumerate(pain_data['potential_pain_points'], 1):
            severity_symbol = {'high': '●', 'medium': '▲', 'low': '○'}
            symbol = severity_symbol.get(pain['severity'].lower(), '•')
            
            story.append(Paragraph(f"<b>{symbol} Pain Point {idx}: {pain['pain_point']}</b>", subheading_style))
            story.append(Paragraph(f"<b>Severity:</b> {pain['severity'].upper()}", normal_style))
            story.append(Paragraph(f"<b>Evidence:</b> {pain['evidence']}", normal_style))
            story.append(Spacer(1, 0.15*inch))
        
        # Solutions Section
        story.append(Paragraph("How Can Help", heading_style))
        
        for idx, solution in enumerate(pain_data['how_we_can_help'], 1):
            story.append(Paragraph(f"<b>Solution {idx}: {solution['our_solution']}</b>", subheading_style))
            story.append(Paragraph(f"<b>Addresses:</b> {solution['addresses_pain_point']}", normal_style))
            story.append(Paragraph(f"<b>Value Proposition:</b> {solution['value_proposition']}", normal_style))
            story.append(Paragraph(f"<b>Implementation Approach:</b> {solution['implementation_approach']}", normal_style))
            story.append(Spacer(1, 0.15*inch))
        
        # Engagement Strategy
        story.append(PageBreak())
        story.append(Paragraph("Engagement Strategy", heading_style))
        
        strategy = pain_data['engagement_strategy']
        story.append(Paragraph(f"<b>Primary Contact:</b> {strategy['primary_contact']}", normal_style))
        story.append(Paragraph(f"<b>Estimated Opportunity Value:</b> {pain_data['estimated_opportunity_value'].upper()}", normal_style))
        story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph("<b>Key Talking Points:</b>", subheading_style))
        for point in strategy['key_talking_points']:
            story.append(Paragraph(f"• {point}", normal_style))
        story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph(f"<b>Differentiation Angle:</b> {strategy['differentiation_angle']}", normal_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Next Steps
        story.append(Paragraph("Recommended Next Steps", heading_style))
        for idx, step in enumerate(pain_data['recommended_next_steps'], 1):
            story.append(Paragraph(f"{idx}. {step}", normal_style))
            story.append(Spacer(1, 0.05*inch))
    
    # Footer
    story.append(Spacer(1, 0.3*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    story.append(Paragraph("Generated by Lead Generation Agent | Powered by Claude AI", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def analyze_company_fit(
    company_name: str,
    target_sectors: List[str],
    target_industries: List[str],
    our_services: str,
    api_key: str
) -> Dict:
    """
    Step 1: Analyze if a company is worth pursuing based on target criteria
    
    This function uses Claude to:
    - Research the company online
    - Determine if it matches our target sectors/industries
    - Assess if it's a good fit for our services
    """
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Construct the analysis prompt
    prompt = f"""You are a lead qualification analyst for a consulting company specializing in data science, AI, and business intelligence.

Our Target Profile:
- Target Sectors: {', '.join(target_sectors)}
- Target Industries: {', '.join(target_industries)}
- Our Services: {our_services}

Company to Analyze: {company_name}

Please analyze this company and provide a JSON response with the following structure:

{{
    "company_name": "string",
    "industry": "string",
    "sector": "string",
    "company_size": "string (estimated employees)",
    "is_good_fit": true/false,
    "fit_score": 0-100,
    "fit_reasoning": "detailed explanation of why this is or isn't a good fit",
    "brief_company_overview": "2-3 sentence overview of what the company does"
}}

Base your analysis on publicly available information about the company. Be thorough and honest in your assessment.

IMPORTANT: Respond ONLY with valid JSON. Do not include any text outside the JSON structure."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract and parse the JSON response
        response_text = message.content[0].text.strip()
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        analysis = json.loads(response_text)
        return {"success": True, "data": analysis}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_pain_point_analysis(
    company_name: str,
    company_overview: str,
    industry: str,
    our_services: str,
    api_key: str
) -> Dict:
    """
    Step 2: Deep dive into company's pain points and how we can help
    
    This function:
    - Identifies potential pain points based on industry and company profile
    - Maps our services to their challenges
    - Suggests approach strategies
    """
    
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""You are a business development analyst specializing in data science, AI, and analytics consulting.

Company Information:
- Name: {company_name}
- Industry: {industry}
- Overview: {company_overview}

Our Services:
{our_services}

Please provide a comprehensive analysis in JSON format:

{{
    "potential_pain_points": [
        {{
            "pain_point": "description",
            "severity": "high/medium/low",
            "evidence": "why we think this is a pain point"
        }}
    ],
    "how_we_can_help": [
        {{
            "our_solution": "which service/capability",
            "addresses_pain_point": "which pain point",
            "value_proposition": "specific benefit",
            "implementation_approach": "brief description"
        }}
    ],
    "engagement_strategy": {{
        "primary_contact": "suggested role to reach out to",
        "key_talking_points": ["point1", "point2", "point3"],
        "differentiation_angle": "what makes our approach unique for them"
    }},
    "estimated_opportunity_value": "small/medium/large/enterprise",
    "recommended_next_steps": ["step1", "step2", "step3"]
}}

Be specific and actionable. Base your analysis on typical challenges in their industry and company profile.

IMPORTANT: Respond ONLY with valid JSON. Do not include any text outside the JSON structure."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        analysis = json.loads(response_text)
        return {"success": True, "data": analysis}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


# UI Layout
st.title("📊 Lead Generation Agent")
st.markdown("**Intelligent lead qualification and analysis powered by AI**")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key input
    api_key = st.text_input(
        "Claude API Key",
        type="password",
        help="Enter your Anthropic API key. Get one at https://console.anthropic.com/"
    )
    
    st.markdown("---")
    
    # Target sectors
    st.subheader("Target Sectors")
    sectors_input = st.text_area(
        "Enter target sectors (one per line)",
        value="Technology\nFinancial Services\nHealthcare\nRetail\nManufacturing\nE-commerce",
        height=120
    )
    target_sectors = [s.strip() for s in sectors_input.split("\n") if s.strip()]
    
    # Target industries
    st.subheader("Target Industries")
    industries_input = st.text_area(
        "Enter target industries (one per line)",
        value="SaaS\nE-commerce\nManufacturing\nConsulting\nFintech\nHealthtech",
        height=120
    )
    target_industries = [i.strip() for i in industries_input.split("\n") if i.strip()]
    
    # Our services
    st.subheader("Our Services")
    our_services = st.text_area(
        "Describe Your services",
        value="""- Data Science Consulting & Strategy
- AI Solutions Development & Implementation
- AI Agents Building (Custom autonomous agents for business processes)
- AI Automation Solutions (Workflow automation, process optimization)
- Power BI Dashboard Development & Training
- Tableau Analytics & Visualization Solutions
- Machine Learning Model Development
- Predictive Analytics Implementation
- Data Pipeline Engineering
- Advanced Analytics & Business Intelligence""",
        height=250
    )

# Main content area
tab1, tab2 = st.tabs(["🔍 Analyze New Lead", "📚 Analysis History"])

with tab1:
    st.header("Analyze a New Company")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        company_name = st.text_input(
            "Company Name",
            placeholder="e.g., TechCorp Inc., Acme Solutions",
            help="Enter the full legal name or common name of the company"
        )
    
    with col2:
        analyze_button = st.button("🚀 Analyze Lead", type="primary", use_container_width=True)
    
    if analyze_button:
        if not api_key:
            st.error("⚠️ Please enter your Claude API key in the sidebar")
        elif not company_name:
            st.error("⚠️ Please enter a company name")
        else:
            # Step 1: Initial fit analysis
            with st.spinner(f"🔍 Step 1/2: Analyzing if {company_name} is a good fit..."):
                fit_result = analyze_company_fit(
                    company_name,
                    target_sectors,
                    target_industries,
                    our_services,
                    api_key
                )
            
            if not fit_result["success"]:
                st.error(f"❌ Error in fit analysis: {fit_result['error']}")
            else:
                fit_data = fit_result["data"]
                
                # Display fit analysis results
                st.success("✅ Step 1 Complete: Fit Analysis")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Fit Score", f"{fit_data['fit_score']}/100")
                with col2:
                    st.metric("Industry", fit_data['industry'])
                with col3:
                    fit_status = "✅ Good Fit" if fit_data['is_good_fit'] else "❌ Poor Fit"
                    st.metric("Status", fit_status)
                
                st.subheader("Company Overview")
                st.info(fit_data['brief_company_overview'])
                
                st.subheader("Fit Assessment")
                st.write(fit_data['fit_reasoning'])
                
                # Step 2: Pain point analysis (only if good fit)
                if fit_data['is_good_fit']:
                    with st.spinner(f"🎯 Step 2/2: Analyzing pain points and opportunities..."):
                        pain_result = generate_pain_point_analysis(
                            company_name,
                            fit_data['brief_company_overview'],
                            fit_data['industry'],
                            our_services,
                            api_key
                        )
                    
                    if not pain_result["success"]:
                        st.error(f"❌ Error in pain point analysis: {pain_result['error']}")
                    else:
                        pain_data = pain_result["data"]
                        
                        st.success("✅ Step 2 Complete: Pain Point Analysis")
                        
                        # Display pain points
                        st.subheader("🎯 Identified Pain Points")
                        for idx, pain in enumerate(pain_data['potential_pain_points'], 1):
                            severity_color = {
                                "high": "🔴",
                                "medium": "🟡",
                                "low": "🟢"
                            }
                            with st.expander(f"{severity_color.get(pain['severity'].lower(), '⚪')} {pain['pain_point']}"):
                                st.write(f"**Severity:** {pain['severity'].upper()}")
                                st.write(f"**Evidence:** {pain['evidence']}")
                        
                        # Display solutions
                        st.subheader("💡 How We Can Help")
                        for idx, solution in enumerate(pain_data['how_we_can_help'], 1):
                            with st.expander(f"Solution {idx}: {solution['our_solution']}"):
                                st.write(f"**Addresses:** {solution['addresses_pain_point']}")
                                st.write(f"**Value Proposition:** {solution['value_proposition']}")
                                st.write(f"**Approach:** {solution['implementation_approach']}")
                        
                        # Engagement strategy
                        st.subheader("📋 Engagement Strategy")
                        strategy = pain_data['engagement_strategy']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Primary Contact:** {strategy['primary_contact']}")
                            st.write(f"**Opportunity Value:** {pain_data['estimated_opportunity_value'].upper()}")
                        
                        with col2:
                            st.write("**Key Talking Points:**")
                            for point in strategy['key_talking_points']:
                                st.write(f"- {point}")
                        
                        st.write(f"**Differentiation:** {strategy['differentiation_angle']}")
                        
                        st.subheader("✅ Recommended Next Steps")
                        for idx, step in enumerate(pain_data['recommended_next_steps'], 1):
                            st.write(f"{idx}. {step}")
                        
                        # Save to history
                        st.session_state.analysis_history.append({
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "company_name": company_name,
                            "fit_data": fit_data,
                            "pain_data": pain_data
                        })
                        
                        st.success("💾 Analysis saved to history!")
                        
                        # PDF Export Button
                        st.markdown("---")
                        st.subheader("📄 Export Report")
                        
                        try:
                            pdf_bytes = generate_pdf_report(company_name, fit_data, pain_data)
                            st.download_button(
                                label="📥 Download PDF Report",
                                data=pdf_bytes,
                                file_name=f"Lead_Analysis_{company_name.replace(' ', '_')}_{time.strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.error(f"Error generating PDF: {str(e)}")
                
                else:
                    st.warning("⚠️ This company is not a good fit based on our target criteria. Pain point analysis skipped.")
                    
                    # Still offer PDF export for rejected leads
                    st.markdown("---")
                    st.subheader("📄 Export Report")
                    
                    try:
                        pdf_bytes = generate_pdf_report(company_name, fit_data, None)
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=pdf_bytes,
                            file_name=f"Lead_Analysis_{company_name.replace(' ', '_')}_{time.strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            type="secondary",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")

with tab2:
    st.header("Analysis History")
    
    if not st.session_state.analysis_history:
        st.info("No analyses yet. Analyze your first lead in the 'Analyze New Lead' tab!")
    else:
        for idx, analysis in enumerate(reversed(st.session_state.analysis_history)):
            with st.expander(f"📊 {analysis['company_name']} - {analysis['timestamp']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Fit Score:** {analysis['fit_data']['fit_score']}/100")
                    st.write(f"**Industry:** {analysis['fit_data']['industry']}")
                    st.write(f"**Good Fit:** {'Yes' if analysis['fit_data']['is_good_fit'] else 'No'}")
                    
                    if 'pain_data' in analysis:
                        st.write(f"**Pain Points Identified:** {len(analysis['pain_data']['potential_pain_points'])}")
                        st.write(f"**Solutions Proposed:** {len(analysis['pain_data']['how_we_can_help'])}")
                        st.write(f"**Opportunity Value:** {analysis['pain_data']['estimated_opportunity_value']}")
                
                with col2:
                    # Export button for historical analysis
                    try:
                        pdf_bytes = generate_pdf_report(
                            analysis['company_name'], 
                            analysis['fit_data'], 
                            analysis.get('pain_data')
                        )
                        st.download_button(
                            label="📥 PDF",
                            data=pdf_bytes,
                            file_name=f"Lead_Analysis_{analysis['company_name'].replace(' ', '_')}_{time.strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key=f"pdf_export_{idx}"
                        )
                    except Exception as e:
                        st.error(f"PDF Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>Powered by Claude Sonnet 4 | Built By Quirky Analytics</p>
        <p style='font-size: 0.9em; color: #666;'>Data Science • AI Solutions • AI Agents • Automation • Power BI • Tableau</p>
    </div>
    """,
    unsafe_allow_html=True
)