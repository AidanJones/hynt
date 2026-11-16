"""Validate browser reports without mistaking desktop emulation for a phone."""
import argparse,json,math
from pathlib import Path
def validate(report):
    assert report['schema_version']==1 and report['complete'] is True
    assert report['tab_remained_visible'] is True
    device=report['device'];assert isinstance(device['declared_physical_phone'],bool)
    assert isinstance(device['label'],str) and device['user_agent'] and device['connection']
    assert [r['year'] for r in report['cases']]==[117,1920]
    def positive(value):assert type(value) in (int,float) and math.isfinite(value) and value>0
    for r in report['cases']:
        positive(r['first_rendered_polity_ms']);positive(r['rendered_fragments'])
        assert r['renderer'] and r['viewport']['width']>0 and r['viewport']['height']>0
        scrub=r['scrub'];assert scrub['updates']==120 and scrub['frame_intervals']==119
        for key in ['mean_frame_ms','p95_frame_ms','observed_fps']:positive(scrub[key])
    assert [r['year'] for r in report['cross_era']]==[1550,1700,1920]
    for r in report['cross_era']:positive(r['rendered_polity_ms']);positive(r['rendered_fragments'])
    return {'device':device['label'],'physical_device_status':'self-reported phone/tablet' if device['declared_physical_phone'] else 'desktop or unverified device',
        'independently_verified_physical_device':False,'frames_valid':True,
        'fps':{str(r['year']):round(r['scrub']['observed_fps'],2) for r in report['cases']}}
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('report',type=Path)
    args=parser.parse_args();print(json.dumps(validate(json.loads(args.report.read_text(encoding='utf-8'))),indent=2))
if __name__=='__main__':main()
