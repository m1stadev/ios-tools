#!/usr/bin/env python3

from flask import Flask
import datetime
import json
import mwclient
import requests

class Wiki(object):
    def __init__(self, device, buildid, boardconfig=''):
        super().__init__()

        self.device = device
        self.buildid = buildid
        self.boardconfig = boardconfig

        self.site = mwclient.Site('www.theiphonewiki.com')
        self.page_name = self.get_keypage()
        self.keys = self.get_keys()

    def get_keypage(self):
        for result in self.site.search(f'{self.buildid} {self.device}'):
            page = self.site.pages[result['title']]
            if page.exists:
                return result.get('title').replace(' ', '_')

            sys.exit(f'[ERROR] No keys exist for device: {self.device}, buildid: {buildid}. Exiting...')

    def parse_page(self):
        self.page = self.site.pages[self.page_name]
        wikikeys = {}

        data = self.page.text().replace(' ', '').replace('|', '').splitlines()
        wiki_version = self.page.text().replace('|', '').splitlines()[1].split('=')[1][1:].replace('[Golden MasterGM]', '[Golden Master|GM]')
        for x in data:
            if x == '' or x == '}}' or x == '{{keys':
                data.pop(data.index(x))
                continue

        for x in data:
            new_str = x.split('=')
            try:
                wikikeys[new_str[0].lower()] = new_str[1]
            except IndexError:
                continue

        wikikeys['version'] = wiki_version

        return wikikeys

    def get_keys(self):
        wiki_keys = self.parse_page()
        keys = []
        rsp = {}
        if self.boardconfig == '' and self.device.lower().endswith(('iphone8,1', 'iphone8,4')):
            return None

        rsp['identifier'] = wiki_keys['device']
        rsp['buildid'] = wiki_keys['build']
        rsp['codename'] = wiki_keys['codename']

        if 'restoreramdisk' in wiki_keys:
            rsp['restoreramdiskexists'] = True
        else:
            rsp['restoreramdiskexists'] = False

        if 'updateramdisk' in wiki_keys:
            rsp['updateramdiskexists'] = True
        else:
            rsp['updateramdiskexists'] = False
                
        for x in ['version', 'device', 'build', 'codename', 'downloadurl']:
            del wiki_keys[x]

        if 'baseband' in wiki_keys:
            del wiki_keys['baseband']
                
        for x in wiki_keys:
            uppercase_component_names = ['RootFS', 'Update Ramdisk', 'Restore Ramdisk', 'AOPFirmware', 'AppleLogo', 'Apple Maggie Firmware Image', 'AudioCodecFirmware', 'BatteryCharging0', 'BatteryCharging1', 'BatteryFull', 'BatteryLow0', 'BatteryLow1', 'DeviceTree', 'DeviceTree2', 'GlyphPlugin', 'Homer', 'iBEC', 'iBEC2', 'iBoot', 'iBoot2', 'iBSS', 'iBSS2', 'ISP', 'Kernelcache', 'LiquidDetect', 'LLB', 'LLB2', 'Multitouch', 'RecoveryMode', 'SEP-Firmware', 'SEP-Firmware']
            lowercase_component_names = ['rootfs', 'updateramdisk', 'restoreramdisk', 'aopfirmware', 'applelogo', 'applemaggie', 'audiocodecfirmware', 'batterycharging0', 'batterycharging1', 'batteryfull', 'batterylow0', 'batterylow1', 'devicetree', 'devicetree2', 'glyphplugin', 'homer', 'ibec', 'ibec2', 'iboot', 'iboot2', 'ibss', 'ibss2', 'isp', 'kernelcache', 'liquiddetect', 'llb', 'llb2', 'multitouch', 'recoverymode', 'sepfirmware', 'sepfirmware2']
            key = {}

            if x.endswith(('key', 'iv', 'kbag', 'model', 'model2')):
                continue

            if self.boardconfig.lower().endswith(('n71map', 'n69uap')) and x.endswith(('devicetree', 'ibec', 'ibss', 'iboot', 'llb', 'sepfirmware')):
                continue

            if self.boardconfig.lower().endswith(('n71ap', 'n69ap')) and x.endswith(('devicetree2', 'ibec2', 'ibss2', 'iboot2', 'llb2', 'sepfirmware2')):
                continue

            if wiki_keys[x].startswith('0'):
                filename = f'{wiki_keys[x]}.dmg'
            else:
                filename = wiki_keys[x]
            
            key["image"] = uppercase_component_names[lowercase_component_names.index(x)]
            key["filename"] = filename #WARNING This is the wrong format! (usually this would be full path instead of just the filename)
            key["date"] = datetime.datetime.now().isoformat()

            non_keys = ['Unknown', 'NotEncrypted']

            if f'{x}iv' in wiki_keys and wiki_keys[f'{x}iv'] not in non_keys:
                key["iv"] = wiki_keys[f'{x}iv']
            else:
                key["iv"] = ''
            if f'{x}key' in wiki_keys and wiki_keys[f'{x}key'] not in non_keys:
                key["key"] = wiki_keys[f'{x}key']
            else:
                key["key"] = ''
            
            if key["key"] == '' or key['iv'] == '':
                key["kbag"] = ''
            else:
                key["kbag"] = key["iv"] + key["key"]

            keys.append(key)
        rsp["keys"] = keys
        return json.dumps(rsp)
        
app = Flask(__name__)

@app.route("/firmware/<device>/<buildid>")
def keys(device, buildid):
    print(f'Getting keys for device: {device}, buildid: {buildid}')
    iphonewiki = Wiki(device, buildid)
    return iphonewiki.keys

@app.route("/firmware/<device>/<boardconfig>/<buildid>")
def keys2(device, boardconfig, buildid):
    print(f'Getting keys for device: {device}({boardconfig}), buildid: {buildid}')
    iphonewiki = Wiki(device, buildid, boardconfig)
    return iphonewiki.keys

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888)
