import copy
import pytest
from pipeline.device_reports import validate

def report():
    return {'schema_version':1,'complete':True,'tab_remained_visible':True,
      'device':{'label':'Test desktop','declared_physical_phone':False,'user_agent':'test','connection':'wifi'},
      'cases':[{'year':y,'first_rendered_polity_ms':1000,'rendered_fragments':10,'renderer':'test',
        'viewport':{'width':390,'height':844},'scrub':{'updates':120,'frame_intervals':119,'mean_frame_ms':17,'p95_frame_ms':20,'observed_fps':58.8}} for y in [117,1920]],
      'cross_era':[{'year':y,'rendered_polity_ms':500,'rendered_fragments':10} for y in [1550,1700,1920]]}

def test_desktop_and_self_reported_phone_are_never_independently_certified():
    data=report();assert validate(data)['physical_device_status']=='desktop or unverified device'
    data['device']['declared_physical_phone']=True
    assert validate(data)['physical_device_status']=='self-reported phone/tablet'
    assert validate(data)['independently_verified_physical_device'] is False

@pytest.mark.parametrize('problem',['hidden','empty-map','partial','nonfinite'])
def test_incomplete_or_invalid_measurements_fail(problem):
    data=report()
    if problem=='hidden':data['tab_remained_visible']=False
    if problem=='empty-map':data['cases'][0]['rendered_fragments']=0
    if problem=='partial':data['complete']=False
    if problem=='nonfinite':data['cases'][0]['scrub']['observed_fps']=float('nan')
    with pytest.raises(AssertionError):validate(data)
