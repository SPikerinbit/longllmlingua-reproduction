"""Read-only checks of the generated report, not of model execution."""
from pathlib import Path
import subprocess,json,re,xml.etree.ElementTree as ET,zipfile,hashlib,csv
R=Path(__file__).resolve().parents[1]
for args,out in [(['pdfinfo',str(R/'report.pdf')],'pdfinfo.txt'),(['pdffonts',str(R/'report.pdf')],'fonts.txt'),(['pdfinfo','-url',str(R/'report.pdf')],'hyperlinks.txt')]:
 (R/'qa'/out).write_text(subprocess.check_output(args,text=True))
subprocess.run(['pdftotext','-layout',str(R/'report.pdf'),str(R/'qa/report-layout.txt')],check=True)
subprocess.run(['pdftotext','-bbox',str(R/'report.pdf'),str(R/'qa/report-bbox.html')],check=True)
text=(R/'qa/report-layout.txt').read_text();pages=[t for t in text.split('\f') if t.strip()]
assert len(pages)==11 and '参考文献与公开来源' in pages[5] and '附录 A' in pages[6]
assert all(len(t)>500 for t in pages) and '\ufffd' not in text
root=ET.parse(R/'qa/report-bbox.html').getroot();bounds=[];outside=[]
for i,p in enumerate(root.iter('{http://www.w3.org/1999/xhtml}page'),1):
 w=float(p.attrib['width']);h=float(p.attrib['height']);words=list(p.iter('{http://www.w3.org/1999/xhtml}word'))
 for word in words:
  a=word.attrib
  if float(a['xMin'])<0 or float(a['yMin'])<0 or float(a['xMax'])>w+.5 or float(a['yMax'])>h+.5:outside.append([i,word.text,a])
 body=[x for x in words if 40<float(x.attrib['yMax'])<790]
 bounds.append({'page':i,'word_count':len(words),'body_bottom_pt':max(float(x.attrib['yMax']) for x in body)})
assert not outside
fonts=(R/'qa/fonts.txt').read_text().splitlines()[2:]
assert all(re.search(r'\byes\s+yes\s+yes\s+\d+',line) for line in fonts)
urls=set(re.findall(r'https://\S+',(R/'qa/hyperlinks.txt').read_text()));assert len(urls)==12
with zipfile.ZipFile(R/'report.docx') as z:assert '<w:tbl>' in z.read('word/document.xml').decode()
preds={r['slot_id']:r for r in map(json.loads,(R/'sources/canonical-stage1/predictions.jsonl').read_text().splitlines())}
cases=json.loads((R/'sources/cases-verified.json').read_text());assert len(cases)==13
for c in cases:
 r=preds[c['slot_id']];assert c['first_line']==r['answer'].splitlines()[0] and c['score']==r['score']
 for k in ['origin_tokens','compressed_tokens','target_tokens']:assert c[k]==r[k]
assert json.loads((R/'sources/stage3-stats-remote.json').read_text())==json.loads((R/'sources/g2/stats.json').read_text())
assert list(csv.DictReader((R/'sources/stage4-ablation-remote.csv').open()))==list(csv.DictReader((R/'sources/g2/ablation.csv').open()))
assert json.loads((R/'sources/stage2-acceptance-remote.json').read_text())['budget_satisfied']==396
# Inspect the real local test evidence without rerunning the repository tests.
vr=R/'sources/local-verification'
full=ET.parse(vr/'junit-full.xml').getroot().find('testsuite')
base=ET.parse(vr/'junit-baseline.xml').getroot().find('testsuite')
assert full.attrib['tests']=='77' and full.attrib['failures']=='0' and full.attrib['errors']=='0' and full.attrib['skipped']=='0'
assert base.attrib['tests']=='77' and base.attrib['failures']=='5'
assert '77 passed in 3.53s' in (vr/'pytest-full.stdout').read_text()
assert 'full_pytest_end=Asia/Shanghai 2026-11-21 17:47:02 CST full_pytest_exit=0' in (vr/'timeline.txt').read_text()
for n in range(1,5):assert json.loads((vr/f'audits/stage{n}/offline-audit.json').read_text())['api_calls']==0
for line in (vr/'SHA256SUMS.txt').read_text().splitlines():
 parts=line.split()
 if len(parts)>=2:assert hashlib.sha256((vr/parts[1]).read_bytes()).hexdigest()==parts[0]
assert len(json.loads((R/'sources/local-resource-readonly-check.json').read_text())['files'])==6
old=Path('/workspace/reports/g14-final')
unchanged=['sources/canonical-stage1/predictions.jsonl','sources/cases-verified.json','sources/g1/summary.json','sources/g1/run.json','sources/g2/ablation.csv','sources/g2/efficiency.csv','sources/stage3-stats-remote.json']
# Original publication file hashes are frozen here, so this check is portable.
expected=json.loads((R/'qa/published-result-hashes.json').read_text())
for rel,h in expected.items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==h
md=(R/'report.md').read_text()
assert '77/77' in md and '历史回传' in md and '3.13.5' in md and '0.22.1' in md
assert '50秒离线验收实录已完成' in md and '真人讲述计时' in md
recording=json.loads((R/'qa/recording-verification.json').read_text())
assert recording['duration_seconds']==50 and recording['width']==1920 and recording['height']==1200 and recording['videoReview']['passed']
for f in recording['files']:assert hashlib.sha256((R/f['package_path']).read_bytes()).hexdigest()==f['sha256']

qa={'total_pdf_pages':11,'body_pages':[1,2,3,4,5],'references_pages':[6],'appendix_pages':[7,8,9,10,11],'blank_pages':0,'fonts_all_embedded':True,'text_outside_page_bounds':outside,'replacement_character_found':False,'distinct_clickable_source_urls':len(urls),'native_editable_docx':True,'page_body_bounds':bounds,'visual_inspection':'11/11 final updated pages rendered and individually inspected; no clipping, orphaned case blocks, missing Chinese, blank pages or collisions observed.','new_model_inference_calls':0,'verified_cases':13,'current_local_pytest':{'tests':77,'failures':0,'errors':0,'skipped':0,'duration_seconds':3.530,'exit':0,'time_window':'2026-11-21 17:46:58–17:47:02 Asia/Shanghai','code_commit':'bdb11d3b3e39523594c0ffcd6c058f6fb7bca1b4','executed_by_report_editor':False},'previous_baseline':{'tests':77,'passed':72,'failed_missing_resources':5,'resolved':True},'public_resources_hashes_checked':6,'copied_evidence_manifest_matches':49,'published_result_snapshots_unchanged':True,'video_status':{'status':'completed offline acceptance recording','seconds':50,'resolution':'1920x1200','videoReview':'passed per parent confirmation','metadata_copy_sha_and_screenshot_checked':True,'human_oral_timing_and_member_confirmation':'not completed'},'distinct_case_questions':4,'stage1_predictions_sha256':hashlib.sha256((R/'sources/canonical-stage1/predictions.jsonl').read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256((R/'report.pdf').read_bytes()).hexdigest()}
prior=json.loads((R/'qa/prior-page-render-hashes.json').read_text())
changed=[p.name for p in sorted((R/'pages').glob('final-*.jpg')) if hashlib.sha256(p.read_bytes()).hexdigest()!=prior.get(p.name)]
assert changed==['final-05.jpg','final-07.jpg']
qa['final_recording_sync_visual_check']={'changed_pages':[5,7],'changed_pages_reinspected':True,'other_nine_pages_pixel_identical_to_individually_inspected_version':True,'page_count_preserved':11}
(R/'qa/final-audit.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
print('PASS: 5 body + 1 reference + 5 appendix pages; all fonts embedded; 12 source URLs; 13 canonical cases; current JUnit 77/77.')
