from bs4 import BeautifulSoup
from pathlib import Path
import json

files = list(Path('./resource/').iterdir())



def get_template() -> (str, str):
    Json = ''
    Component = ''
    with open(Path('./json_template.json'), 'r') as o:
        tmp = o.readlines()
        for t in tmp:
            Json += t
    with open(Path('./component_template.json'), 'r') as o:
        tmp = o.readlines()
        for t in tmp:
            Component += t
    return Json, Component


def get_original_info(f: Path) -> (list, list, list):
    ids = list()
    names = list()
    input_tags = list()
    with open(f, 'r+') as of:
        soup = BeautifulSoup(of, 'html.parser')
        finding = soup.find(name='section', id='findings')
        if finding:
            inputs = finding.find_all(name=['input', 'textarea'])
            for i in inputs:
                names.append(i.findPrevious(name='label').text)
                input_tags.append(i)
                ids.append(i.get('id'))
    for i in range(len(names)):
        names[i] = names[i].replace(' ', '.')
    return ids, names, input_tags


def generate_script() -> str:
    script_str = ''
    script_str += f'var json = {json.dumps(Json, indent=2)};\n'
    script_str += '''var fhirUrl = "https://hapi.fhir.org/baseR4";\n
    function postData(jsonString, type) {
      var xhttp = new XMLHttpRequest();
      var url = fhirUrl +"/"+type;
      xhttp.open("POST", url, false);
      xhttp.setRequestHeader("Content-type", 'application/json+fhir');
      xhttp.onreadystatechange = function () {
          if (this.readyState == 4) // && this.status == 201)
          {
              ret = JSON.parse(this.responseText);
              alert(this.responseText);
          }
      };
      var data = JSON.stringify(jsonString);
      xhttp.send(data);
    }\n'''
    script_str += 'function Submit(){\n'
    for i in range(len(Json['component'])):
        script_str += f'\tjson.component[{i}].valueString=document.getElementById("{ids[i]}").value;\n'
    script_str += '\tpostData(json,"Observation")\n}'
    return script_str


def generate_new_html() -> str:
    with open(f, 'r+') as of:
        soup = BeautifulSoup(of, 'html.parser')
        soup.head.script.decompose()
        submit_btn = soup.new_tag('input', type='submit', onClick='Submit()')
        script = soup.new_tag('script', type='text/javascript')
        script.string = script_str
        soup.body.append(submit_btn)
        soup.html.append(script)
        return str(soup.prettify(formatter='html'))


for f in files:
    Json, Component = get_template()
    ids, names, input_tags = get_original_info(f)
    Json = json.loads(Json)
    for i in range(len(names)):
        tmp_component = json.loads(Component)
        tmp_component['code']['coding'][0]['code'] = names[i]
        Json['component'].append(tmp_component)
    script_str = generate_script()
    result = generate_new_html()

    file_path = Path(f'./result/{f.name}')
    if not file_path.exists():
        Path.touch(file_path)
    with open(file_path, 'w') as f2:
        f2.write(result)
