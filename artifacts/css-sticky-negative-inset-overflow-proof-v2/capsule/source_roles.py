import hashlib,json

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(c,s):
    if not c:raise RuntimeError('source role: '+s)
PINS={
 'combined-before':'2a0794213ffad4d35d96b915b0fc858e2bfb18ddf74b20e4884a2d6b6f0f3b4b',
 'combined-after':'0e3b5f3e85e41a9e65164c489acfba58d12634e9a6658df71dcd3bf141ab4096',
 'standalone-before':'877d9e663bd76a750537c19fe02d2f357be6407bab87484366f0766799ccc817',
 'standalone-after':'52c7c219259af222e620c9913a0d2993c8fcf7cdea31b3d76b7b734e8fbf1a78'}
HEADER_BEFORE='2df4e7ceb481101ed13ff125c2aa4b86bf939fd2efc3f80791754dfe955c4a6b'
HEADER_AFTER='e4c44b8a11a2b474d3d03f3c4d4628e63ee60570d5be4ee373b63d1be831722e'
PATCH='68c14d1d2b0fdb2fad21efc9e670a6ddcdf40740c1e84230225f7bae57251484'

def authenticate(root):
    path='layout/generic/StickyScrollContainer.cpp';header='layout/generic/StickyScrollContainer.h'
    read=lambda name:json.loads((root/'inputs'/name).read_text())
    for role,pin in PINS.items():require(sha(root/'inputs'/(role+'.cpp'))==pin,role+' bytes')
    require(len(set(PINS.values()))==4,'distinct genuine variants')
    for name,pin in [('before-StickyScrollContainer.h',HEADER_BEFORE),('combined-final-StickyScrollContainer.h',HEADER_AFTER),('standalone-StickyScrollContainer.h',HEADER_AFTER)]:require(sha(root/'inputs'/name)==pin,name)
    for phase,role in [('baseline','combined-before'),('candidate','combined-after'),('standalone','standalone-after')]:
        receipt=read(phase+'-wpt-v1-RUN.json')
        for side in ['before','after']:
            require(receipt[side][path]==PINS[role],phase+' '+side+' native identity')
            require(receipt[side][header]==(HEADER_BEFORE if phase=='baseline' else HEADER_AFTER),phase+' '+side+' header identity')
        require(receipt['exit']==(1 if phase=='baseline' else 0),phase+' execution')
    packaging=read('PACKAGING.json');require(packaging['patch_sha256']==PATCH and sha(root/'inputs/fix.patch')==PATCH,'standalone patch identity')
    require(packaging['live_pins'][path]==PINS['combined-after'],'packaged combined role')
    require(len(packaging['checks'])==2,'packaging base roster')
    for check in packaging['checks']:
        require(check['before'][path]==PINS['standalone-before'] and check['after'][path]==PINS['standalone-after'] and check['apply_reverse'],'standalone base roles')
    transfer=read('STANDALONE-SOURCE-TRANSFER.json');restore=read('COMBINED-SOURCE-RESTORED.json')
    require(transfer['before'][path]==PINS['combined-after'] and transfer['after'][path]==PINS['standalone-after'],'standalone transfer')
    require(restore['before'][path]==PINS['standalone-after'] and restore['after'][path]==PINS['combined-after'] and restore['combined_source_restored'],'combined restoration')
    return {'sources':PINS,'header_before':HEADER_BEFORE,'header_after':HEADER_AFTER,'patch':PATCH,'live_source_read':False}
