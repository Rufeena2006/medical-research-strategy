from src import config
from src.pubmed_client import parse_pubmed_xml
from src.screening import classify_design, screen_record

SAMPLE_XML = """<?xml version="1.0"?>
<PubmedArticleSet>
<PubmedArticle>
  <MedlineCitation><PMID>111</PMID>
    <Article>
      <Journal><Title>Test Journal</Title>
        <JournalIssue><PubDate><Year>2023</Year></PubDate></JournalIssue></Journal>
      <ArticleTitle>Semaglutide and weight loss in adults with obesity</ArticleTitle>
      <Abstract><AbstractText Label="BACKGROUND">Adults with obesity received semaglutide.</AbstractText></Abstract>
      <Language>eng</Language>
      <PublicationTypeList><PublicationType>Randomized Controlled Trial</PublicationType></PublicationTypeList>
    </Article>
  </MedlineCitation>
  <PubmedData><ArticleIdList><ArticleId IdType="doi">10.1000/test</ArticleId></ArticleIdList></PubmedData>
</PubmedArticle>
<PubmedArticle>
  <MedlineCitation><PMID>222</PMID>
    <Article>
      <Journal><Title>Rodent Journal</Title>
        <JournalIssue><PubDate><MedlineDate>2022 Jan-Feb</MedlineDate></PubDate></JournalIssue></Journal>
      <ArticleTitle>Liraglutide in obese mice</ArticleTitle>
      <Abstract><AbstractText>Obese mice were given liraglutide.</AbstractText></Abstract>
      <Language>eng</Language>
      <PublicationTypeList><PublicationType>Journal Article</PublicationType></PublicationTypeList>
    </Article>
  </MedlineCitation>
  <PubmedData><ArticleIdList/></PubmedData>
</PubmedArticle>
</PubmedArticleSet>"""


def test_queries_are_balanced():
    for name, q in config.QUERIES.items():
        assert q.count("(") == q.count(")"), name
    assert config.RETRIEVAL_QUERY in config.QUERIES


def test_parse_xml():
    recs = parse_pubmed_xml(SAMPLE_XML)
    assert len(recs) == 2
    assert recs[0]["pmid"] == "111" and recs[0]["doi"] == "10.1000/test"
    assert recs[0]["abstract"].startswith("BACKGROUND:")
    assert recs[1]["year"] == "2022"


def test_screening():
    recs = parse_pubmed_xml(SAMPLE_XML)
    assert screen_record(recs[0])[0] == "include_candidate"
    assert screen_record(recs[1]) == ("exclude", "animal study")
    assert classify_design(recs[0]["pub_types"]) == "RCT / clinical trial"


def test_report_builds(tmp_path):
    from src.generate_report import build
    out = build("Test Author", tmp_path, tmp_path / "r.docx")
    assert out.exists() and out.stat().st_size > 10000
