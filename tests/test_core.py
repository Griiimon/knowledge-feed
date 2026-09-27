from pathlib import Path
import json
from knowledge_feed.content import load_article
from knowledge_feed.deduplication import is_duplicate
from knowledge_feed.models import Article
from knowledge_feed.site import build_site
from knowledge_feed.topic_selector import select_topic

def article(**overrides):
    base=dict(id='roman-concrete',title='Why Roman Concrete Heals Cracks',category='Ancient Engineering',date='2026-09-01',reading_time=2,seed='Roman concrete',tags=['rome'],status='published',body='Hello **world**.',summary='A summary.',sources=[]); base.update(overrides); return Article(**base)
def test_duplicate_detection():
    assert is_duplicate('Roman concrete', 'Different title', [article()])
    assert is_duplicate('Other', 'How Roman Concrete Heals Cracks', [article()])
    assert not is_duplicate('Pulsars', 'How Pulsars Keep Time', [article()])
def test_topic_rotation():
    categories=[{'name':'A','description':'a','seeds':['used','fresh']},{'name':'B','description':'b','seeds':['new']}]
    chosen=select_topic(categories,[article(category='A',seed='used')],999)
    assert chosen.category == 'B'
def test_article_validation(tmp_path):
    p=tmp_path/'x.md'; p.write_text('---\nid: x\ntitle: T\ncategory: C\ndate: "2026-01-01"\nreading_time: 1\nseed: S\ntags: [x]\nstatus: published\n---\n\nBody')
    assert load_article(p).title == 'T'
def test_site_escapes_model_content(tmp_path):
    root=tmp_path; (root/'config').mkdir(); (root/'content/articles').mkdir(parents=True); (root/'templates').mkdir(); (root/'static').mkdir()
    source=Path(__file__).parents[1]
    for f in ('config/config.yaml',): (root/f).write_text((source/f).read_text())
    for d in ('templates','static'):
        for f in (source/d).iterdir(): (root/d/f.name).write_text(f.read_text())
    (root/'content/articles/x.md').write_text('---\nid: x\ntitle: "<script>x</script>"\ncategory: C\ndate: "2026-01-01"\nreading_time: 1\nseed: S\ntags: [x]\nstatus: published\nsummary: "<b>bad</b>"\n---\n\n<script>alert(1)</script>')
    out=build_site(root); text=(out/'articles/x/index.html').read_text()
    assert '<script>alert' not in text and '&lt;script&gt;' in text

def test_generation_with_fake_client():
    from knowledge_feed.generator import generate_article
    from knowledge_feed.models import Topic
    class FakeClient:
        def __init__(self): self.calls=0
        def chat(self, prompt):
            self.calls += 1
            if self.calls == 1:
                return json.dumps({'title':'A focused topic','summary':'Brief summary','body_markdown':'word ' * 300,'tags':['test'],'sources':[{'title':'Reference','url':'https://example.com'}]})
            return json.dumps({'approved':True,'quality_score':8,'issues':[],'suggested_changes':[]})
    result=generate_article(FakeClient(), Topic('Test','test topic','seed'), {'min_words':300,'max_words':700,'review_enabled':True,'approval_threshold':1}, 5)
    assert result.status == 'published' and result.reading_time == 2
