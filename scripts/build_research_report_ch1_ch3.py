from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont


OUT = Path("reports/Hierarchical_Multi_Agent_RAG_Report_Chapters_1_to_4.docx")
FIGURE_DIR = Path("reports/figures")


TITLE = "A Hierarchical Multi Agent Framework for Reliable RAG with Self Reflection and Graph Based Reasoning"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def style_table(table):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for row_idx, row in enumerate(table.rows):
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.08
                for run in p.runs:
                    run.font.name = "Calibri"
                    run.font.size = Pt(10)
            if row_idx == 0:
                set_cell_shading(cell, "F2F4F7")
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.bold = True


def set_styles(doc):
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12

    for style_name, size, color, before, after in [
        ("Heading 1", 16, "2E74B5", 16, 8),
        ("Heading 2", 13, "2E74B5", 12, 6),
        ("Heading 3", 12, "1F4D78", 8, 4),
    ]:
        style = styles[style_name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True


def add_title_page(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run(TITLE)
    r.bold = True
    r.font.size = Pt(18)
    r.font.name = "Calibri"
    r.font.color.rgb = RGBColor.from_string("1F4D78")

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run("Research Project Report")
    r.font.size = Pt(13)
    r.font.name = "Calibri"

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(24)
    r = p.add_run("Chapters 1 to 4")
    r.font.size = Pt(12)
    r.font.name = "Calibri"

    meta = [
        ("Student Name", "Huang Xuan"),
        ("Project Area", "Retrieval Augmented Generation and Multi Agent Systems"),
        ("Prepared For", "Research Project Report"),
        ("Date", "June 2026"),
    ]
    table = doc.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Item"
    table.rows[0].cells[1].text = "Details"
    for k, v in meta:
        row = table.add_row().cells
        row[0].text = k
        row[1].text = v
    style_table(table)
    doc.add_page_break()


def add_para(doc, text):
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return p


def add_heading(doc, text, level=1):
    doc.add_heading(text, level=level)


def add_figure(doc, image_path, caption, width=6.2):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(image_path), width=Inches(width))
    cap = doc.add_paragraph(caption)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(8)
    for run in cap.runs:
        run.italic = True
        run.font.size = Pt(10)
    return p


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    for i, h in enumerate(headers):
        table.rows[0].cells[i].text = h
    for row_data in rows:
        row = table.add_row().cells
        for i, value in enumerate(row_data):
            row[i].text = str(value)
    style_table(table)
    doc.add_paragraph()
    return table


def _font(size=22, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _box(draw, xy, text, fill, outline="#2B4C7E", text_fill="#172033", font_size=22):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=12, fill=fill, outline=outline, width=2)
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=_font(font_size))[2] < (x2 - x1 - 28):
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    line_h = font_size + 7
    total_h = len(lines) * line_h
    y = y1 + ((y2 - y1) - total_h) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=_font(font_size))
        draw.text((x1 + (x2 - x1 - (bbox[2] - bbox[0])) / 2, y), line, fill=text_fill, font=_font(font_size))
        y += line_h


def _arrow(draw, start, end, color="#2B4C7E"):
    draw.line([start, end], fill=color, width=3)
    x1, y1 = start
    x2, y2 = end
    if x2 >= x1:
        pts = [(x2, y2), (x2 - 12, y2 - 7), (x2 - 12, y2 + 7)]
    else:
        pts = [(x2, y2), (x2 + 12, y2 - 7), (x2 + 12, y2 + 7)]
    draw.polygon(pts, fill=color)


def ensure_report_figures():
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    title_font = _font(30, bold=True)
    label_font = _font(20, bold=True)

    architecture = FIGURE_DIR / "system_architecture.png"
    img = Image.new("RGB", (1600, 980), "#FFFFFF")
    d = ImageDraw.Draw(img)
    d.text((60, 38), "Overall Architecture of the Proposed Agentic RAG System", fill="#17324D", font=title_font)
    layers = [
        ("Presentation Layer", 90, "#EAF4FF"),
        ("Agent Orchestration Layer", 250, "#F2F7ED"),
        ("Retrieval Layer", 520, "#FFF4E5"),
        ("Storage and Graph Layer", 700, "#F6EEFA"),
        ("Model Layer", 850, "#EEF2F7"),
    ]
    for label, y, fill in layers:
        d.rounded_rectangle((50, y, 1550, y + 120), radius=18, fill=fill, outline="#CBD5E1", width=2)
        d.text((75, y + 18), label, fill="#17324D", font=label_font)
    _box(d, (680, 115, 920, 175), "Streamlit Web UI", "#FFFFFF")
    nodes = [
        ("Planner", 140), ("Query Decomposer", 310), ("Retrieval Coordinator", 520),
        ("Validator", 750), ("Synthesis", 950), ("Writer", 1130), ("Critic", 1300), ("Reliability Gate", 1420),
    ]
    for text, x in nodes:
        _box(d, (x, 290, x + 145, 360), text, "#FFFFFF", font_size=18)
    for i in range(len(nodes) - 1):
        x = nodes[i][1] + 145
        nx = nodes[i + 1][1]
        _arrow(d, (x, 325), (nx, 325))
    d.line([(800, 175), (800, 225), (210, 225), (210, 290)], fill="#2B4C7E", width=3)
    d.polygon([(210, 290), (203, 278), (217, 278)], fill="#2B4C7E")
    _arrow(d, (1370, 360), (1195, 360))
    d.text((1235, 374), "self reflection", fill="#2B4C7E", font=_font(16))
    _box(d, (295, 555, 510, 630), "Vector Search", "#FFFFFF")
    _box(d, (655, 555, 870, 630), "BM25 Keyword Search", "#FFFFFF")
    _box(d, (1015, 555, 1230, 630), "Graph Search", "#FFFFFF")
    _arrow(d, (590, 360), (405, 555))
    _arrow(d, (592, 360), (760, 555))
    _arrow(d, (595, 360), (1120, 555))
    _box(d, (375, 735, 610, 805), "ChromaDB Vector Store", "#FFFFFF")
    _box(d, (995, 735, 1230, 805), "Knowledge Graph", "#FFFFFF")
    _arrow(d, (405, 630), (490, 735))
    _arrow(d, (760, 630), (490, 735))
    _arrow(d, (1120, 630), (1120, 735))
    _box(d, (375, 875, 610, 935), "BGE Embeddings", "#FFFFFF")
    _box(d, (995, 875, 1230, 935), "DeepSeek LLM", "#FFFFFF")
    _arrow(d, (490, 875), (490, 805))
    d.text((1245, 892), "used by planner, validator, writer and critic", fill="#52616B", font=_font(15))
    img.save(architecture)

    pipeline = FIGURE_DIR / "baseline_vs_agentic_pipeline.png"
    img = Image.new("RGB", (1600, 820), "#FFFFFF")
    d = ImageDraw.Draw(img)
    d.text((60, 40), "Baseline RAG Compared with the Proposed Agentic RAG Pipeline", fill="#17324D", font=title_font)
    d.rounded_rectangle((60, 135, 1540, 330), radius=18, fill="#F8FAFC", outline="#CBD5E1", width=2)
    d.text((90, 160), "Baseline Vector-only RAG", fill="#17324D", font=label_font)
    b_nodes = [("Query", 260), ("Embed", 470), ("Vector Top-K", 680), ("Single LLM Call", 920), ("Answer", 1190)]
    for text, x in b_nodes:
        _box(d, (x, 220, x + 170, 285), text, "#FFFFFF", font_size=18)
    for i in range(len(b_nodes) - 1):
        _arrow(d, (b_nodes[i][1] + 170, 252), (b_nodes[i + 1][1], 252))
    d.rounded_rectangle((60, 405, 1540, 740), radius=18, fill="#F2F7ED", outline="#CBD5E1", width=2)
    d.text((90, 430), "Proposed Hierarchical Agentic RAG", fill="#17324D", font=label_font)
    a_nodes = [
        ("Query", 120, 505), ("Planner", 295, 505), ("Decompose", 470, 505), ("Hybrid Retrieval", 645, 505),
        ("Validator", 845, 505), ("Synthesis", 1020, 505), ("Writer", 1195, 505), ("Critic", 1365, 505),
    ]
    for text, x, y in a_nodes:
        _box(d, (x, y, x + 145, y + 65), text, "#FFFFFF", font_size=17)
    for i in range(len(a_nodes) - 1):
        _arrow(d, (a_nodes[i][1] + 145, 537), (a_nodes[i + 1][1], 537))
    _box(d, (545, 640, 725, 705), "Vector + BM25 + Graph", "#FFFFFF", font_size=17)
    _box(d, (1230, 640, 1450, 705), "Reliability Gate + Final Answer", "#FFFFFF", font_size=17)
    _arrow(d, (720, 570), (635, 640))
    _arrow(d, (1435, 570), (1340, 640))
    img.save(pipeline)

    results = FIGURE_DIR / "complex_benchmark_results.png"
    img = Image.new("RGB", (1500, 900), "#FFFFFF")
    d = ImageDraw.Draw(img)
    d.text((60, 40), "Complex Reasoning Benchmark Results", fill="#17324D", font=title_font)
    metrics = [
        ("Thesis Score", 0.850, 0.921),
        ("GT Coverage", 0.766, 0.795),
        ("Missing Info", 0.833, 1.000),
        ("Multi-hop", 0.838, 0.865),
        ("Graph Reasoning", 0.882, 0.923),
        ("Evidence Support", 0.843, 0.829),
    ]
    x0, y0 = 330, 145
    max_w = 900
    d.text((80, 118), "Metric", fill="#17324D", font=label_font)
    d.text((x0, 110), "Baseline", fill="#52616B", font=label_font)
    d.text((x0 + 420, 110), "Agentic", fill="#1B6B52", font=label_font)
    for i, (label, base, agent) in enumerate(metrics):
        y = y0 + 20 + i * 115
        d.text((80, y + 12), label, fill="#17324D", font=_font(21, bold=True))
        d.rounded_rectangle((x0, y, x0 + int(max_w * base), y + 34), radius=8, fill="#A8B3BD")
        d.rounded_rectangle((x0, y + 45, x0 + int(max_w * agent), y + 79), radius=8, fill="#2A9D75")
        d.text((x0 + int(max_w * base) + 12, y - 1), f"{base:.3f}", fill="#52616B", font=_font(19))
        d.text((x0 + int(max_w * agent) + 12, y + 44), f"{agent:.3f}", fill="#1B6B52", font=_font(19))
    d.text((80, 835), "Note: Agentic improves reliability-oriented metrics, while latency remains higher and keyword F1 is slightly lower.", fill="#52616B", font=_font(20))
    img.save(results)

    return {
        "architecture": architecture,
        "pipeline": pipeline,
        "results": results,
    }


def add_reference(doc, runs):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(-0.25)
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(6)
    for text, italic in runs:
        run = p.add_run(text)
        run.italic = italic
        run.font.name = "Calibri"
        run.font.size = Pt(11)
    return p


def chapter_1(doc):
    add_heading(doc, "Chapter 1: Introduction", 1)

    add_heading(doc, "1.1 Introduction", 2)
    add_para(doc, "Retrieval augmented generation has become an important approach for building question answering systems that need to respond with information grounded in external documents. Instead of depending only on the internal knowledge of a language model, a RAG system first retrieves relevant text from a knowledge source and then uses that retrieved context to generate an answer. This design is useful for academic papers, technical manuals, company documents and other information sources where the answer should be traceable to the original material.")
    add_para(doc, "Although RAG has improved the usefulness of large language models, many simple RAG systems still rely on a fixed pipeline. A typical baseline system embeds the user query, retrieves several vector similar chunks and sends them to a language model. This approach is easy to implement, but it can fail when the question is broad, multi step, relational or requires comparison across different parts of a document. It may also produce answers without clear citations, or use retrieved context only weakly. These limitations reduce trust in the generated answer.")
    add_para(doc, "This project proposes a hierarchical multi agent framework for reliable RAG with self reflection and graph based reasoning. The system separates the RAG process into several agents, including planning, query decomposition, retrieval coordination, validation, synthesis, answer writing, criticism and a reliability gate. Retrieval is not limited to one method. The proposed system combines vector search, keyword search and optional graph based retrieval so that evidence can be collected from different perspectives before answer generation.")
    add_para(doc, "The implementation is built as a document question answering system with Streamlit as the user interface, ChromaDB for vector storage, BGE embeddings for semantic retrieval, BM25 for keyword retrieval, NetworkX for knowledge graph support and DeepSeek as the language model. A vector only RAG baseline is included so that the proposed method can be compared with a simpler pipeline. The evaluation evidence includes baseline comparison, RAGAS based WriterAgent validation, ablation study, unit tests and case study outputs. The results show that the proposed method improves several reliability oriented metrics, especially in complex reasoning tasks, while increasing response latency.")

    add_heading(doc, "1.2 Problem Statement", 2)
    add_para(doc, "The main problem addressed in this project is the lack of reliability in simple RAG based document question answering systems. In a standard vector only RAG pipeline, retrieved chunks are selected mainly through semantic similarity. This can be insufficient when the user asks a question that requires exact terms, document level understanding, comparison between sections or relationships between concepts. If the retrieval step is weak, the language model may generate an answer that is incomplete, poorly grounded or missing citations.")
    add_para(doc, "Another problem is that many RAG systems do not contain a clear quality control mechanism. Once the retrieved context is passed to the language model, the answer is often returned directly to the user. There may be no validation of whether the retrieved context is sufficient, no review of whether the answer is properly supported and no final check that citations match available evidence. This creates a risk of unsupported or over confident responses.")
    add_para(doc, "The third problem is that graph based relationships are not usually included in basic RAG systems. Documents often contain entities, methods, results, limitations and relationships among them. Pure vector retrieval may locate similar text, but it does not explicitly model relationships between entities or sections. As a result, questions that require relational reasoning may not be handled well.")
    add_para(doc, "Therefore, there is a need for a RAG framework that can coordinate different retrieval methods, review the quality of retrieved evidence, generate citation aware answers and apply a reliability check before returning the final answer. This project addresses the problem by designing and implementing a hierarchical multi agent RAG framework that is more reliable than a naive vector only baseline.")

    add_heading(doc, "1.3 Research Questions", 2)
    add_para(doc, "This project is guided by the following research questions.")
    questions = [
        "How can a hierarchical multi agent architecture be used to improve the reliability of a RAG based document question answering system?",
        "How can hybrid retrieval using vector search, keyword search and graph based reasoning improve the quality of retrieved evidence compared with a vector only baseline?",
        "How can self reflection and reliability checking reduce unsupported answers and improve citation based grounding?",
        "What trade offs appear when the proposed agentic RAG framework is compared with a simple baseline RAG system in terms of citation rate, context usage, answer completeness and latency?",
    ]
    for q in questions:
        p = doc.add_paragraph(q, style="List Number")
        p.paragraph_format.space_after = Pt(4)

    add_heading(doc, "1.4 Research Objectives", 2)
    add_para(doc, "The objectives of this research are as follows.")
    objectives = [
        "To design a hierarchical multi agent RAG framework that separates planning, retrieval, validation, synthesis, writing, criticism and reliability checking into clear functional agents.",
        "To implement a hybrid retrieval mechanism that combines semantic vector retrieval, BM25 keyword retrieval and graph based retrieval support.",
        "To develop a self reflection process that allows generated answers to be reviewed and improved through a critic agent and reliability gate.",
        "To build a working document question answering application that allows users to upload documents and ask questions through a web interface.",
        "To evaluate the proposed framework against a vector only baseline using citation rate, context usage, average answer length, retrieval count, response latency, RAGAS validation evidence and ablation analysis.",
    ]
    for obj in objectives:
        p = doc.add_paragraph(obj, style="List Number")
        p.paragraph_format.space_after = Pt(4)

    add_heading(doc, "1.5 Scope", 2)
    add_para(doc, "The scope of this project is limited to the design, implementation and evaluation of a document based RAG system. The system supports uploaded documents such as PDF, DOCX and text files. The core task is question answering over indexed document content. The system does not aim to train a new large language model. Instead, it focuses on the orchestration of retrieval, reasoning and answer verification around an existing language model.")
    add_para(doc, "The system includes a Streamlit interface, document loading, hierarchical chunking, embedding generation, ChromaDB vector storage, BM25 keyword indexing, optional knowledge graph construction, multi agent orchestration, citation aware answer generation and benchmark comparison against a baseline. The evaluation uses controlled document grounded test sets rather than private or unrelated uploaded files. The report also uses project evidence from the GitHub repository, including the RAGAS evaluation report, the ablation report, generated benchmark tables and case study files.")
    add_para(doc, "Several limitations are acknowledged. The graph reasoning component depends on entity extraction quality and may not always be available if the required natural language processing model is not installed. The evaluation uses a controlled synthetic corpus because the project is a graduation level system prototype. The system measures practical reliability indicators such as citation rate, context usage, missing information accuracy and graph reasoning success. RAGAS is used as supplementary validation for the WriterAgent and production gate, while the end to end thesis benchmark uses custom metrics because full RAGAS scoring is slower and less stable in the local environment.")

    add_heading(doc, "1.6 Time Schedule", 2)
    add_para(doc, "The project was completed through a sequence of design, implementation, evaluation and report writing activities. The schedule below summarises the main phases of the work. It is included to show how the research moved from problem identification to a working prototype and final benchmark analysis.")
    add_table(doc, ["Phase", "Main Activities", "Output"], [
        ("Phase 1", "Reviewed RAG, multi agent systems, self reflection and graph based reasoning literature.", "Research background and problem definition"),
        ("Phase 2", "Designed the baseline RAG pipeline and the proposed hierarchical multi agent workflow.", "Architecture model and methodology"),
        ("Phase 3", "Implemented document ingestion, vector retrieval, BM25 retrieval, graph search support and Streamlit interface.", "Working RAG application prototype"),
        ("Phase 4", "Implemented planner, query decomposer, retrieval coordinator, validator, synthesis agent, writer, critic and reliability gate.", "Complete agentic RAG workflow"),
        ("Phase 5", "Prepared controlled thesis documents, benchmark datasets, baseline comparison and complex reasoning evaluation.", "Experiment tables, summaries and case studies"),
        ("Phase 6", "Analysed results, prepared figures and wrote the research report.", "Final report chapters and GitHub project evidence"),
    ])

    add_heading(doc, "1.7 Conclusion", 2)
    add_para(doc, "This chapter introduced the research background, problem statement, research questions, objectives, scope and time schedule. The main motivation of this project is to improve the reliability of RAG based document question answering by moving beyond a simple vector only pipeline. The proposed solution is a hierarchical multi agent RAG framework that combines hybrid retrieval, self reflection and graph based reasoning support. The next chapter reviews related work and identifies the open issues that motivate the proposed design.")


def chapter_2(doc):
    add_heading(doc, "Chapter 2: Literature Review", 1)

    add_heading(doc, "2.1 Introduction", 2)
    add_para(doc, "This chapter reviews the literature related to retrieval augmented generation, transformer based language models, multi agent systems, self reflection mechanisms and graph based reasoning. The purpose of the review is to identify the strengths and weaknesses of existing methods and to explain how they inform the design of the proposed system.")
    add_para(doc, "The review shows that RAG improves the factual grounding of language models, but reliability remains a major concern. Retrieval quality, citation faithfulness, multi hop reasoning and answer verification are still open problems. Recent research has therefore explored hybrid retrieval, agentic workflows, reflective generation and graph enhanced retrieval. These directions form the foundation of this project.")

    add_heading(doc, "2.2 Literature Review", 2)
    add_heading(doc, "2.2.1 Transformer Based Language Models", 3)
    add_para(doc, "The Transformer architecture introduced by Vaswani et al. changed the development of natural language processing by replacing recurrent sequence modelling with attention mechanisms (Vaswani et al., 2017). Self attention allows a model to capture relationships between tokens across long sequences more efficiently than earlier recurrent approaches. Modern large language models are built on this foundation and can generate fluent answers across many domains.")
    add_para(doc, "However, language models also have limitations. Their internal knowledge can be outdated, incomplete or difficult to verify. They may generate responses that sound plausible even when the answer is not supported by a source. For document question answering, this means that a language model should not be used alone. It should be grounded in external evidence retrieved from the target document.")

    add_heading(doc, "2.2.2 Retrieval Augmented Generation", 3)
    add_para(doc, "Retrieval augmented generation was proposed to connect neural generation with external knowledge sources. In a RAG system, the user query is used to retrieve relevant passages, and the language model generates an answer based on those passages. Lewis et al. showed that retrieval can improve knowledge intensive tasks by allowing the model to access external information during generation (Lewis et al., 2020).")
    add_para(doc, "A basic RAG pipeline usually consists of document chunking, embedding, vector search and answer generation. This design is useful, but it depends heavily on the quality of retrieved chunks. If the retriever misses important evidence, the generated answer may be incomplete. If the retriever returns irrelevant chunks, the generator may include unsupported statements. Therefore, retrieval quality and answer grounding are central issues in RAG system design.")

    add_heading(doc, "2.2.3 Hybrid Retrieval", 3)
    add_para(doc, "Vector retrieval is good at semantic matching, while keyword retrieval is useful for exact terms, names, symbols and technical phrases. In practice, both methods have different strengths. Semantic search may retrieve conceptually related passages even when exact words differ, but it can miss exact details. Keyword search may locate exact phrases, but it can fail when the question is paraphrased.")
    add_para(doc, "Hybrid retrieval combines these approaches to improve evidence coverage. In this project, vector search is implemented with BGE embeddings and ChromaDB, while keyword search is implemented with BM25, a ranking method developed from the probabilistic relevance framework (Robertson & Zaragoza, 2009). The retrieval coordinator gathers evidence from both sources and the synthesis agent deduplicates and ranks the retrieved chunks. This improves the chance that the writer receives useful context.")

    add_heading(doc, "2.2.4 Multi Agent RAG Systems", 3)
    add_para(doc, "Agent based systems divide a complex task into smaller roles. In the context of RAG, different agents can handle planning, retrieval, validation, synthesis and answer writing. This design is more flexible than a fixed single pipeline because each agent can focus on a specific responsibility.")
    add_para(doc, "A hierarchical agent structure is suitable for reliable RAG because the system can first decide how complex the query is, then select or coordinate retrieval strategies, and finally review whether the answer is acceptable. This project uses a planner, query decomposer, retrieval coordinator, validator, synthesis agent, writer, critic and reliability gate. The design makes the reasoning process more transparent and easier to evaluate.")

    add_heading(doc, "2.2.5 Self Reflection and Answer Verification", 3)
    add_para(doc, "Self reflection in language model systems refers to the process of reviewing and improving an answer after initial generation. In RAG, reflection is useful because the generated answer should be checked against retrieved evidence. Self reflective retrieval work shows that retrieval, generation and critique can be connected to improve factuality (Asai et al., 2023). A critic can review whether the answer is accurate, relevant, complete and properly cited. If the answer is weak, the writer can regenerate it with feedback.")
    add_para(doc, "This project includes a critic agent and a deterministic reliability gate. The critic agent reviews answer quality, while the reliability gate checks whether an answer has citations, whether citations are valid and whether retrieved context exists. This makes the final answer more controlled than a single generation step.")

    add_heading(doc, "2.2.6 Graph Based Reasoning", 3)
    add_para(doc, "Graph based reasoning represents information as entities and relationships. A knowledge graph can support questions that require relational understanding, such as how one concept connects to another or which evidence supports a claim. In document question answering, graph based retrieval can complement vector search by using entity paths and relationships. Recent GraphRAG work also shows the value of graph structures for global sensemaking over text collections (Microsoft Research, 2024).")
    add_para(doc, "In this project, the graph component uses entity extraction, relationship extraction and a NetworkX based knowledge graph. The graph search agent can be included in the retrieval swarm when a graph is available. This is particularly relevant for complex or relational questions, although its performance depends on the quality of entity and relationship extraction.")

    add_heading(doc, "2.3 Open Issues and Challenges", 2)
    add_para(doc, "Several issues remain open in current RAG systems. First, retrieval quality is still difficult to guarantee. A retriever may return passages that are semantically close but not sufficient for the answer. This is especially common for broad document level questions or questions requiring comparison across sections.")
    add_para(doc, "Second, citation reliability remains a challenge. A generated answer may include citations that are too general, missing or not directly tied to the claim being made. For academic and professional document question answering, this weakens trust in the system.")
    add_para(doc, "Third, many RAG systems have limited reasoning over relationships. Vector retrieval retrieves text based on similarity, but it does not explicitly represent entity links or document structure. Graph based reasoning can help, but building a useful graph from arbitrary documents is still difficult.")
    add_para(doc, "Fourth, there is a trade off between reliability and latency. Additional agents and quality checks can improve answer control, but they also increase response time. A practical system must balance answer quality with usability.")
    add_para(doc, "Finally, evaluation is challenging. Automatic metrics can measure citation rate, context usage and latency, but deeper qualities such as faithfulness and answer usefulness may require stronger reference answers or human review. RAGAS provides a useful framework for evaluating RAG pipelines using faithfulness, answer relevancy, context precision and context recall (Es et al., 2023). This project addresses this issue by combining baseline comparison, RAGAS based validation, ablation study and case studies.")

    add_heading(doc, "2.4 Conclusion", 2)
    add_para(doc, "This chapter reviewed related work in transformer models, RAG, hybrid retrieval, multi agent systems, self reflection and graph based reasoning. The review shows that a reliable RAG system should not depend only on vector retrieval and a single language model call. Instead, it should coordinate multiple retrieval methods, validate evidence, review generated answers and check citations. These findings support the design of the proposed hierarchical multi agent RAG framework, which is described in the next chapter.")


def chapter_3(doc):
    figures = ensure_report_figures()
    add_heading(doc, "Chapter 3: Methodology", 1)

    add_heading(doc, "3.1 Introduction", 2)
    add_para(doc, "This chapter describes the research methodology used to design, implement and evaluate the proposed RAG system. The methodology follows a design and development research approach. The project begins with problem identification and literature review, then proceeds to system design, implementation, testing and evaluation. The main output is a working prototype that can be compared with a baseline RAG system.")
    add_para(doc, "The proposed system is evaluated through two controlled multi document benchmarks designed for this project. The first benchmark contains 32 general document grounded questions and is used as a broad baseline comparison. The second benchmark contains 40 complex reasoning questions and is used as the main stress benchmark because it is more closely aligned with the project title. The evaluation compares a naive vector only baseline with the complete hierarchical agentic RAG workflow. The metrics include ground truth keyword coverage, missing information accuracy, multi hop coverage, graph reasoning success, citation rate, citation based context usage, answer length, latency and number of retrieved chunks. These metrics are chosen because the project aims to improve reliability and evidence grounding rather than only produce fluent answers.")

    add_heading(doc, "3.2 Research Methodology", 2)
    add_para(doc, "The research methodology consists of five main phases. The first phase is requirement analysis, where the limitations of simple RAG systems are identified. The second phase is system design, where the hierarchical agent architecture and retrieval workflow are planned. The third phase is implementation, where the system is developed using Python, Streamlit, ChromaDB, BM25, BGE embeddings, NetworkX, LangGraph and DeepSeek. The fourth phase is evaluation, where the proposed system is compared with a vector only baseline. The final phase is analysis, where the results are interpreted in relation to the research objectives.")
    add_para(doc, "The baseline system is a naive vector only RAG pipeline. It embeds the query, retrieves the top chunks using vector similarity and sends the retrieved chunks to the writer model. It does not include planning, hybrid retrieval, graph retrieval, validation, synthesis, critic review or a reliability gate.")
    add_para(doc, "The proposed system uses a hierarchical agent design. In the full workflow, the planner assesses query complexity, the query decomposer handles complex questions, the retrieval coordinator manages vector, keyword and graph retrieval agents, the validator checks retrieval sufficiency, the synthesis agent merges evidence, the writer generates a cited answer, the critic reviews the answer and the reliability gate performs deterministic final checks. The final thesis benchmark uses this complete workflow with self reflection regeneration disabled during measurement, so that critic scores and validation behaviour are recorded without making the runtime impractical.")
    add_figure(doc, figures["pipeline"], "Figure 3.1: Baseline RAG compared with the proposed hierarchical agentic RAG pipeline.", width=6.5)

    add_heading(doc, "3.3 Architecture Model", 2)
    add_para(doc, "The architecture is divided into four layers. The presentation layer contains the Streamlit web interface, where users upload documents and ask questions. The ingestion and storage layer loads documents, splits them into hierarchical chunks, generates embeddings and stores them in ChromaDB. The retrieval layer includes vector search, BM25 keyword search and optional graph search. The orchestration layer coordinates agents and controls the answer generation process.")
    add_para(doc, "The baseline architecture follows a simple route from query embedding to vector search and answer generation. The proposed architecture expands this route by adding a retrieval coordinator, synthesis stage and reliability gate. In the complete architecture, additional agents such as planner, validator and critic can be activated for more controlled reasoning. This layered design allows the system to be tested in both a faster benchmark mode and a complete workflow mode.")
    add_figure(doc, figures["architecture"], "Figure 3.2: Overall architecture of the proposed Agentic RAG system, adapted from the project GitHub architecture documentation.", width=6.5)
    add_table(doc, ["Component", "Role in the System"], [
        ("Streamlit interface", "Provides document upload, chat interaction and evaluation display."),
        ("Document loader and chunker", "Loads PDF, DOCX and text documents, then creates parent and child chunks."),
        ("BGE embeddings", "Generates semantic vectors for document chunks and user questions."),
        ("ChromaDB", "Stores vector embeddings and supports semantic retrieval."),
        ("BM25 keyword retrieval", "Retrieves passages using exact term matching and keyword relevance."),
        ("Retrieval coordinator", "Combines vector, keyword and optional graph retrieval results."),
        ("Synthesis agent", "Deduplicates and ranks retrieved chunks before answer generation."),
        ("Writer agent", "Generates a natural language answer with inline citations."),
        ("Critic agent", "Reviews answer quality and can request regeneration in the full workflow."),
        ("Reliability gate", "Checks citations, context availability and answer safety before final output."),
    ])
    add_para(doc, "The system architecture supports the project title because it is hierarchical, agent based, retrieval focused and designed for reliability. The graph based reasoning component is included through a graph search agent and knowledge graph support, while self reflection is represented by the critic agent and regeneration loop in the full workflow.")

    add_heading(doc, "3.4 Dataset", 2)
    add_para(doc, "The final evaluation uses a controlled thesis benchmark rather than private personal files or unrelated uploaded documents. Four English DOCX documents were generated specifically for the research title. The documents cover enterprise RAG design, hierarchical multi agent workflow, graph reasoning over a technical incident and evaluation with ablation analysis. This design makes the benchmark directly aligned with the project topic.")
    add_table(doc, ["Document", "Focus", "Purpose"], [
        ("thesis_doc_01_rag_system_design.docx", "RAG system design", "Tests vector retrieval, BM25, citation policy and failure cases."),
        ("thesis_doc_02_multi_agent_workflow.docx", "Hierarchical multi agent workflow", "Tests planner, decomposer, retrieval coordinator, validator, writer, critic and reliability gate reasoning."),
        ("thesis_doc_03_graph_reasoning_case_study.docx", "Graph reasoning case study", "Tests entity relationships, dependencies, risks and multi hop reasoning."),
        ("thesis_doc_04_evaluation_and_ablation_report.docx", "Evaluation and ablation report", "Tests table interpretation, baseline comparison, RAGAS style metrics, latency trade off and missing information handling."),
    ])
    add_para(doc, "The general benchmark contains eight questions per document, giving a total of 32 test cases. The categories are summary, fact extraction, method explanation, comparison, relationship reasoning, evidence selection, limitations and missing information. Each case stores the target document filename, the question, a ground truth answer, the category and the difficulty level. During evaluation, both the baseline and proposed model are forced to retrieve from the same target document, which prevents cross document contamination and makes the comparison fair.")
    add_table(doc, ["General Benchmark Category", "Cases", "Purpose"], [
        ("summary", "4", "Checks whether the system can summarise the main purpose of a document."),
        ("fact extraction", "4", "Checks whether the system can extract explicit details and numbers."),
        ("method explanation", "4", "Checks whether the system can explain a process or mechanism."),
        ("comparison", "4", "Checks whether the system can contrast two methods, causes or trade offs."),
        ("relationship reasoning", "4", "Checks whether the system can reason over connected entities or workflow roles."),
        ("evidence selection", "4", "Checks whether the system can select evidence that supports a claim."),
        ("limitations", "4", "Checks whether the system can identify constraints and open issues."),
        ("missing information", "4", "Checks whether the system avoids inventing details not present in the document."),
    ])
    add_para(doc, "The complex reasoning benchmark contains 40 stress test questions. It reduces simple fact extraction and focuses on multi hop relationship reasoning, graph dependency reasoning, evidence selection, missing information handling, self reflection reliability reasoning and evaluation or ablation explanation. This design is not intended to make the baseline look weak artificially. Instead, it tests the problem setting where a hierarchical multi agent RAG framework should be useful.")
    add_table(doc, ["Complex Benchmark Category", "Cases", "Purpose"], [
        ("multi hop relationship reasoning", "5", "Checks whether the answer connects several related evidence points."),
        ("graph dependency reasoning", "8", "Checks whether the answer follows dependency chains and entity relationships."),
        ("evidence selection", "6", "Checks whether the system selects evidence that directly supports a claim."),
        ("missing information handling", "6", "Checks whether the system refuses to invent absent details."),
        ("self reflection reliability reasoning", "6", "Checks whether validation, critic review and reliability gate behaviour can be explained."),
        ("evaluation and ablation explanation", "9", "Checks whether experimental tables, trade offs and component removal effects can be interpreted."),
    ])
    add_para(doc, "The generated corpus is indexed independently in data/chroma_thesis_eval, and the keyword index is stored separately as data/bm25_thesis_eval.pkl. A separate graph file is also created for the graph reasoning cases. This avoids pollution from earlier Streamlit uploads and allows the experiment to be reproduced from a clean controlled corpus.")
    add_table(doc, ["Benchmark Artifact", "Location"], [
        ("Generated document corpus", "data/thesis_corpus"),
        ("General evaluation dataset", "data/evaluation/thesis_multi_document_dataset.json"),
        ("Complex reasoning dataset", "data/evaluation/thesis_complex_reasoning_dataset.json"),
        ("Chroma vector index", "data/chroma_thesis_eval"),
        ("BM25 keyword index", "data/bm25_thesis_eval.pkl"),
        ("Knowledge graph", "data/graphs/thesis_multi_document_graph.pkl"),
        ("General benchmark answers and metrics", "results/thesis_multi_document"),
        ("Complex benchmark answers and metrics", "results/thesis_complex_reasoning"),
    ])

    add_heading(doc, "3.4.1 Project Evidence Files", 3)
    add_para(doc, "The implementation is supported by several evidence files in the project repository. These files are important because they show that the system is not only a conceptual design, but also an implemented and evaluated prototype.")
    add_table(doc, ["Evidence File", "Purpose in the Report"], [
        ("docs/RAGAS_EVALUATION_REPORT.md", "Records the RAGAS validation of the WriterAgent, production gate logic and test coverage."),
        ("docs/ABLATION_REPORT.md", "Summarises the component level ablation study for hierarchical chunking and graph search."),
        ("data/ablation_results.json", "Stores the raw ablation measurements used to compare retrieval variants."),
        ("data/evaluation/thesis_multi_document_dataset.json", "Defines the 32 document grounded questions used in the final thesis benchmark."),
        ("results/thesis_multi_document/custom_metrics_summary.md", "Stores the final baseline versus agentic comparison using custom reliability metrics."),
        ("results/thesis_multi_document/experiment_table.csv", "Stores per question latency, retrieved chunk counts, keyword coverage and optional RAGAS score columns."),
        ("results/thesis_multi_document/case_studies", "Contains six side by side baseline and proposed model answers for qualitative discussion."),
    ])

    add_heading(doc, "3.4.2 RAGAS WriterAgent Validation", 3)
    add_para(doc, "In addition to the latest thesis benchmark, the repository contains a RAGAS evaluation report for the WriterAgent. RAGAS evaluates RAG outputs using faithfulness, answer relevancy, context precision and context recall. In this project, the RAGAS validation was used to test whether the WriterAgent could generate grounded answers, cite context correctly and refuse to invent missing information.")
    add_table(doc, ["Case", "Scenario", "Relevancy", "Faithfulness", "Precision", "Recall", "Overall"], [
        ("1", "Complete information available", "0.925", "1.000", "1.000", "1.000", "0.981"),
        ("2", "Partial information with missing inventor detail", "0.000", "1.000", "1.000", "1.000", "0.750"),
        ("3", "Information completely missing", "0.000", "1.000", "1.000", "1.000", "0.750"),
    ])
    add_para(doc, "The most important result from this validation is that faithfulness reached 1.000 in all three cases. This means the tested WriterAgent answers were supported by the provided context. The answer relevancy score was 0.000 in the partial and missing information cases because the model correctly refused to provide information that was absent from the context. This is not treated as a failure in this project, because a faithful refusal is preferable to a fluent but unsupported answer.")
    add_para(doc, "The production gate therefore uses a two level decision rule. Faithfulness is treated as a hard gate, while the overall score is used as a soft gate only when the answer is not an honest non answer. The system also detects phrases that indicate missing information, such as statements that the provided documents do not contain the requested detail. This design supports the reliability goal of the project.")

    add_heading(doc, "3.4.3 Unit Test Coverage", 3)
    add_para(doc, "The RAGAS evaluation pipeline is supported by 17 unit tests. These tests use mocked scores so that the evaluation logic can be checked without repeated external scoring calls. The test suite verifies initialization, metric ranges, batch evaluation, quality detection, edge cases, dataset loading and threshold logic.")
    add_table(doc, ["Test Group", "Number of Tests", "Main Purpose"], [
        ("Initialization", "2", "Checks evaluator setup and metric loading."),
        ("Basic evaluation behaviour", "4", "Checks score ranges, overall score calculation and batch evaluation."),
        ("Quality detection", "3", "Checks that grounded answers score better than hallucinated answers."),
        ("Edge cases", "3", "Checks empty context, short answers and many context chunks."),
        ("Dataset handling", "3", "Checks JSON dataset loading and missing file errors."),
        ("Threshold rules", "2", "Checks pass and fail behaviour under production thresholds."),
    ])
    add_para(doc, "All 17 tests passed in the repository report. This supports the claim that the evaluation pipeline is implemented and reproducible, not only described in theory.")

    add_heading(doc, "3.4.4 Ablation Study", 3)
    add_para(doc, "An ablation study was used to examine the effect of individual retrieval components. The raw ablation file compares a baseline retrieval method, hierarchical chunking, a hybrid setting and graph search. The results show that hierarchical chunking produced the same average retrieval score as the baseline on the small test document, but reduced average retrieval time from 0.510 seconds to 0.367 seconds. This represents a practical speed improvement, although the accuracy benefit requires larger documents to be measured more clearly.")
    add_table(doc, ["Method", "Average Time", "Average Score", "Average Chunks", "Interpretation"], [
        ("Baseline", "0.510 seconds", "0.664", "2.0", "Reference retrieval setting."),
        ("Hierarchical chunking", "0.367 seconds", "0.664", "2.0", "Same score with faster retrieval on the test document."),
        ("Hybrid retrieval", "0.357 seconds", "0.664", "2.0", "Similar measured score in the stored ablation run."),
        ("Graph search", "2.551 seconds", "2.594", "0.4", "Triggered only when relationship evidence is available."),
    ])
    add_para(doc, "The graph search result should be interpreted carefully. It is not designed to replace vector retrieval for every question. Instead, it is most useful for relationship based questions where entities and links can be extracted from the document. The ablation results therefore support keeping graph reasoning as a complementary component in the agentic retrieval workflow.")

    add_heading(doc, "3.4.5 Case Study Outputs", 3)
    add_para(doc, "The project also produces case study files that compare the baseline and proposed model answer for selected questions. For example, in the first case study, the baseline answer mentions several details from the paper but gives a less direct summary of the document topic. The proposed model states more clearly that the document introduces the Transformer architecture, which relies entirely on attention mechanisms and removes recurrence and convolution from the sequence transduction model. These case studies are useful for later discussion because they show qualitative differences that are not fully captured by aggregate metrics.")

    add_heading(doc, "3.5 Conclusion", 2)
    add_para(doc, "This chapter explained the research methodology, system architecture, dataset and evaluation evidence. The methodology follows a practical design and development approach, where a baseline RAG system and a proposed hierarchical agentic RAG system are implemented and compared. The architecture combines document ingestion, vector storage, hybrid retrieval, graph retrieval support, validation, synthesis, citation aware generation and reliability checking. The final evaluation uses four controlled documents, a 32 question general benchmark and a 40 question complex reasoning benchmark. The evaluation evidence includes the baseline comparison, RAGAS WriterAgent validation, unit tests, ablation results and case study outputs. These findings provide the basis for the evaluation chapter that follows.")


def chapter_4(doc):
    figures = ensure_report_figures()
    add_heading(doc, "Chapter 4: Results and Discussion", 1)

    add_heading(doc, "4.1 Introduction", 2)
    add_para(doc, "This chapter presents two sets of experimental results for the proposed hierarchical multi agent RAG framework. The first experiment is a general benchmark with 32 document grounded questions. The second experiment is a complex reasoning stress benchmark with 40 questions. The stress benchmark is treated as the main experiment because it directly tests the project title: reliable RAG, self reflection, hierarchical multi agent control and graph based reasoning.")
    add_para(doc, "The baseline used vector retrieval with a cited writer. The proposed workflow used planning, query decomposition, hybrid retrieval, graph search support, validation, synthesis, writing, critic review and a reliability gate. In both experiments, the baseline and proposed model were restricted to retrieve from the same target document for each question. This prevents cross document contamination and makes the comparison fair.")

    add_heading(doc, "4.2 General Benchmark Results", 2)
    add_para(doc, "The 32 question general benchmark was retained as a broad comparison. It contains summary, fact extraction, method explanation, comparison, relationship reasoning, evidence selection, limitation and missing information questions. The result shows that the baseline is competitive when the questions are relatively direct.")
    add_table(doc, ["Metric", "Baseline", "Proposed Agentic RAG", "Difference"], [
        ("Ground truth keyword coverage", "0.782", "0.789", "+0.007"),
        ("Citation rate", "0.938", "0.938", "+0.000"),
        ("Citation based context usage", "0.578", "0.375", "-0.203"),
        ("Average word count", "50.906", "51.594", "+0.688"),
        ("Average latency", "10.28 seconds", "55.60 seconds", "+45.32 seconds"),
        ("Average retrieved chunks", "2.0", "3.0", "+1.0"),
    ])
    add_para(doc, "The proposed model achieved slightly higher ground truth keyword coverage than the baseline, increasing from 0.782 to 0.789. This is only a small improvement. The citation rate was equal for both systems. The proposed workflow retrieved more chunks, but it also required much higher latency. Therefore, the general benchmark does not show that agentic RAG is always better. Instead, it shows that a simple baseline can be strong for direct document questions.")

    add_heading(doc, "4.3 Complex Reasoning Benchmark Results", 2)
    add_para(doc, "The complex reasoning benchmark was created to test the tasks that the proposed framework is designed for. It contains 40 questions focused on multi hop reasoning, graph dependency reasoning, evidence selection, missing information handling, self reflection reliability reasoning and evaluation or ablation explanation. The benchmark completed all 40 questions without baseline or agentic runtime errors. A retrieval audit confirmed that all retrieved contexts came from the correct target document.")
    add_table(doc, ["Metric", "Baseline", "Proposed Agentic RAG", "Difference"], [
        ("Thesis complex reasoning score", "0.850", "0.921", "+0.071"),
        ("Ground truth keyword F1", "0.464", "0.459", "-0.005"),
        ("Ground truth keyword coverage", "0.766", "0.795", "+0.030"),
        ("Missing information accuracy", "0.833", "1.000", "+0.167"),
        ("Multi hop coverage", "0.838", "0.865", "+0.027"),
        ("Graph reasoning success", "0.882", "0.923", "+0.041"),
        ("Evidence support rate", "0.843", "0.829", "-0.014"),
        ("Citation rate", "0.975", "0.975", "+0.000"),
        ("Average latency", "13.92 seconds", "70.05 seconds", "+56.13 seconds"),
        ("Average retrieved chunks", "5.0", "8.8", "+3.8"),
    ])
    add_figure(doc, figures["results"], "Figure 4.1: Complex reasoning benchmark comparison between baseline RAG and the proposed agentic RAG workflow.", width=6.4)
    add_para(doc, "The main result is that the proposed system achieved a higher thesis complex reasoning score, increasing from 0.850 to 0.921. This score is a weighted reliability score aligned with the research objectives. It gives weight to missing information handling, graph reasoning success, multi hop coverage, ground truth coverage and citation presence. The score is used because the project is not mainly about simple fact extraction. It is about reliable RAG under complex reasoning conditions.")
    add_para(doc, "The proposed system also improved ground truth keyword coverage from 0.766 to 0.795, missing information accuracy from 0.833 to 1.000, multi hop coverage from 0.838 to 0.865 and graph reasoning success from 0.882 to 0.923. These results support the claim that the proposed framework is stronger for reliability oriented reasoning tasks. However, ground truth keyword F1 was slightly lower for the proposed model, decreasing from 0.464 to 0.459. This means the agentic answer was not always more concise or keyword efficient. The result should be interpreted honestly: the proposed system is stronger on the reliability dimensions targeted by the thesis, but it does not dominate every automatic metric.")

    add_heading(doc, "4.4 Category Level Results", 2)
    add_table(doc, ["Category", "Questions", "Baseline F1", "Agentic F1", "Difference", "Baseline Coverage", "Agentic Coverage"], [
        ("evaluation and ablation explanation", "9", "0.467", "0.498", "+0.030", "0.764", "0.778"),
        ("evidence selection", "6", "0.498", "0.465", "-0.033", "0.811", "0.815"),
        ("graph dependency reasoning", "8", "0.463", "0.506", "+0.043", "0.832", "0.822"),
        ("missing information handling", "6", "0.552", "0.533", "-0.020", "0.751", "0.702"),
        ("multi hop relationship reasoning", "5", "0.424", "0.380", "-0.044", "0.734", "0.863"),
        ("self reflection reliability reasoning", "6", "0.372", "0.323", "-0.050", "0.675", "0.802"),
    ])
    add_para(doc, "At category level, the proposed system shows its clearest F1 improvement in graph dependency reasoning and evaluation or ablation explanation. It also improves coverage for multi hop relationship reasoning and self reflection reliability reasoning. These categories are closely linked to the system design because they require multiple evidence pieces, component relationships or reliability process explanation.")
    add_para(doc, "The baseline remains stronger in some F1 categories because it often produces compact answers that match reference keywords efficiently. This is a useful finding rather than a failure. It shows that agentic RAG should not replace a baseline for every easy question. A practical deployment could route simple fact questions to the baseline and complex reliability questions to the agentic workflow.")

    add_heading(doc, "4.5 Document Level Results", 2)
    add_table(doc, ["Document", "Questions", "Baseline F1", "Agentic F1", "Difference", "Baseline Coverage", "Agentic Coverage"], [
        ("RAG system design", "9", "0.482", "0.397", "-0.085", "0.774", "0.775"),
        ("Multi agent workflow", "11", "0.403", "0.388", "-0.015", "0.637", "0.734"),
        ("Graph reasoning case study", "11", "0.472", "0.531", "+0.059", "0.813", "0.826"),
        ("Evaluation and ablation report", "9", "0.511", "0.518", "+0.008", "0.856", "0.852"),
    ])
    add_para(doc, "The strongest document level result is the graph reasoning case study. Agentic F1 increased from 0.472 to 0.531, and coverage increased from 0.813 to 0.826. This is important because the graph document contains dependency chains and relationship based reasoning, which are the clearest target use cases for the proposed framework. The multi agent workflow document also shows a strong coverage improvement from 0.637 to 0.734, even though F1 remains slightly lower.")

    add_heading(doc, "4.6 Case Study Discussion", 2)
    add_para(doc, "The case study files in results/thesis_complex_reasoning/case_studies provide qualitative evidence beyond the aggregate metrics. Several cases show the proposed system using more retrieved chunks and producing answers that connect multiple evidence points. The graph reasoning cases are especially relevant because they ask the system to trace dependency chains rather than only repeat a single sentence.")
    add_table(doc, ["Case Focus", "Why It Matters"], [
        ("Missing information", "The proposed workflow achieved 1.000 missing information accuracy, showing that it consistently refused to invent absent details."),
        ("Graph dependency reasoning", "The proposed workflow improved graph reasoning success from 0.882 to 0.923 and retrieved broader evidence chains."),
        ("Multi hop reasoning", "The proposed workflow improved multi hop coverage from 0.838 to 0.865 and often collected more evidence chunks."),
        ("Evaluation and ablation explanation", "The proposed workflow improved F1 from 0.467 to 0.498 in this category, showing stronger interpretation of experiment results."),
        ("Reliability process explanation", "The proposed workflow records planner strategy, validation score, critic score and retrieval rounds, which provides process evidence that the baseline does not have."),
    ])
    add_para(doc, "A useful example is the graph reasoning document. Questions about dependencies such as Billing API, Cache Layer, Search Index, Audit Dashboard and Compliance Review require the answer to connect several entities. The proposed workflow can decompose the question, retrieve through multiple routes and validate evidence sufficiency before writing. This makes the answer process more transparent than a single vector retrieval call.")

    add_heading(doc, "4.7 RAGAS Validation and Ablation Evidence", 2)
    add_para(doc, "The final complex benchmark uses custom metrics as the primary evidence because full RAGAS scoring over all baseline and agentic answers was too slow and unstable for the local environment. RAGAS is still used as supplementary validation evidence for the WriterAgent and reliability gate. The repository RAGAS report shows faithfulness of 1.000 in complete, partial and missing information cases. This supports the claim that the writer can produce context grounded answers and that honest refusal is preferable to hallucination.")
    add_para(doc, "The ablation evidence also supports the design. Hierarchical chunking and hybrid retrieval provide alternative evidence channels, while graph search is most useful when entity relationships are available. The complex benchmark confirms this interpretation. Graph based reasoning and missing information handling are where the proposed architecture shows the strongest reliability advantage.")

    add_heading(doc, "4.8 Discussion", 2)
    add_para(doc, "The main finding is that the proposed hierarchical multi agent RAG framework is not a universal replacement for a fast baseline. The general benchmark shows that vector only RAG is competitive for direct questions. The complex reasoning benchmark shows that the proposed framework is more meaningful when the task requires missing information detection, graph reasoning, multi hop evidence coverage and reliability process control.")
    add_para(doc, "The latency cost is significant. The proposed workflow averaged 70.05 seconds in the complex benchmark, compared with 13.92 seconds for the baseline. This is expected because the proposed workflow includes planning, decomposition, hybrid retrieval, validation, synthesis and critic review. In practical use, the system should route simple questions to a faster path and reserve the complete workflow for high reliability tasks.")
    add_para(doc, "The results also reveal a limitation of the current graph search implementation. Some graph searches failed because the entity extractor did not identify enough entities in the decomposed subquery. This does not invalidate the project, but it shows that graph based reasoning depends on entity extraction quality. Future work should improve entity linking and query rewriting for graph search.")

    add_heading(doc, "4.9 Conclusion", 2)
    add_para(doc, "This chapter presented the general benchmark and the complex reasoning benchmark. The general benchmark shows only a small average improvement, which confirms that a simple baseline remains strong for direct document questions. The complex benchmark provides stronger evidence for the research title. The proposed system improved the thesis complex reasoning score from 0.850 to 0.921, missing information accuracy from 0.833 to 1.000, multi hop coverage from 0.838 to 0.865 and graph reasoning success from 0.882 to 0.923. The trade off is higher latency and slightly weaker ground truth keyword F1. Overall, the results support the feasibility of a hierarchical multi agent framework for reliable RAG with self reflection and graph based reasoning, especially for complex reliability tasks.")


def references(doc):
    add_heading(doc, "References", 1)
    add_reference(doc, [
        ("Asai, A., Wu, Z., Wang, Y., Sil, A., & Hajishirzi, H. (2023). Self-RAG: Learning to retrieve, generate, and critique through self-reflection. ", False),
        ("arXiv.", True),
        (" https://arxiv.org/abs/2310.11511", False),
    ])
    add_reference(doc, [
        ("Es, S., James, J., Espinosa-Anke, L., & Schockaert, S. (2023). RAGAS: Automated evaluation of retrieval augmented generation. ", False),
        ("arXiv.", True),
        (" https://arxiv.org/abs/2309.15217", False),
    ])
    add_reference(doc, [
        ("Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Kuttler, H., Lewis, M., Yih, W., Rocktaschel, T., Riedel, S., & Kiela, D. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. ", False),
        ("Advances in Neural Information Processing Systems, 33", True),
        (", 9459-9474. https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html", False),
    ])
    add_reference(doc, [
        ("Microsoft Research. (2024). GraphRAG: Improving global search via dynamic community selection. https://www.microsoft.com/en-us/research/project/graphrag/", False),
    ])
    add_reference(doc, [
        ("Robertson, S., & Zaragoza, H. (2009). The probabilistic relevance framework: BM25 and beyond. ", False),
        ("Foundations and Trends in Information Retrieval, 3", True),
        ("(4), 333-389. https://doi.org/10.1561/1500000019", False),
    ])
    add_reference(doc, [
        ("Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A., Kaiser, L., & Polosukhin, I. (2017). Attention is all you need. ", False),
        ("Advances in Neural Information Processing Systems, 30", True),
        (". https://proceedings.neurips.cc/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html", False),
    ])


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    set_styles(doc)
    add_title_page(doc)
    chapter_1(doc)
    doc.add_page_break()
    chapter_2(doc)
    doc.add_page_break()
    chapter_3(doc)
    doc.add_page_break()
    chapter_4(doc)
    doc.add_page_break()
    references(doc)
    doc.core_properties.author = "Huang Xuan"
    doc.core_properties.last_modified_by = "Huang Xuan"
    doc.core_properties.title = TITLE
    doc.core_properties.subject = "Research Project Report"
    doc.core_properties.comments = ""
    doc.core_properties.keywords = "RAG, multi agent system, self reflection, graph based reasoning"
    doc.core_properties.category = "Research Project Report"
    doc.save(OUT)
    print(OUT.resolve())


if __name__ == "__main__":
    main()
