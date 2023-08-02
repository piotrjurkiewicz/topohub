import importlib.resources
import json

import pytest as pytest

import topohub.generate

def test_generate_gabriel():
    graph = topohub.generate.GabrielGenerator.generate_topo(25, 25)
    assert graph['directed'] is False
    assert graph['multigraph'] is False
    assert graph['graph']['name'] == '25'
    assert graph['graph']['demands'] == {}

    org = {'directed': False, 'multigraph': False, 'graph': {'name': '25', 'demands': {}},
           'nodes': [{'id': 'R0', 'pos': (188.48115119519298, 463.3942538631604)},
                     {'id': 'R1', 'pos': (421.7233695661211, 107.02288497602169)},
                     {'id': 'R2', 'pos': (435.85405612271876, 318.23087287534577)},
                     {'id': 'R3', 'pos': (21.19606307910038, 476.4860300622295)},
                     {'id': 'R4', 'pos': (127.84183410823357, 152.950490134722)},
                     {'id': 'R5', 'pos': (212.04007825311461, 294.25700701262974)},
                     {'id': 'R6', 'pos': (62.1958247419368, 343.3386524356115)},
                     {'id': 'R7', 'pos': (416.12026168828817, 256.1595252285978)},
                     {'id': 'R8', 'pos': (397.23040888174734, 312.4899801444396)},
                     {'id': 'R9', 'pos': (179.3386657302935, 234.69719113652377)},
                     {'id': 'R10', 'pos': (51.992065769851045, 486.55322877152645)},
                     {'id': 'R11', 'pos': (318.0147620963196, 49.1128958782206)},
                     {'id': 'R12', 'pos': (291.38807712605256, 207.21298960303818)},
                     {'id': 'R13', 'pos': (94.69819693315796, 80.46624667435532)},
                     {'id': 'R14', 'pos': (230.37175861171588, 35.184925062400566)},
                     {'id': 'R15', 'pos': (281.53890397158676, 257.46391205398623)},
                     {'id': 'R16', 'pos': (63.53995848216232, 437.580570459992)},
                     {'id': 'R17', 'pos': (20.26328646418918, 86.03603421640416)},
                     {'id': 'R18', 'pos': (217.78065265969477, 247.06792314105613)},
                     {'id': 'R19', 'pos': (252.3656251053449, 241.36930868882106)},
                     {'id': 'R20', 'pos': (28.804644272073244, 408.1682618516225)},
                     {'id': 'R21', 'pos': (141.4245708631205, 23.869894397222147)},
                     {'id': 'R22', 'pos': (204.14203714612768, 407.22209355537865)},
                     {'id': 'R23', 'pos': (314.4130966318092, 228.61712432824683)},
                     {'id': 'R24', 'pos': (238.9999066946048, 109.81289084704876)}],
           'links': [{'source': 'R0', 'target': 'R16', 'dist': 127.57996663815867},
                     {'source': 'R0', 'target': 'R22', 'dist': 58.3144488305541},
                     {'source': 'R1', 'target': 'R7', 'dist': 149.2418583498508},
                     {'source': 'R1', 'target': 'R11', 'dist': 118.78148888035041},
                     {'source': 'R1', 'target': 'R12', 'dist': 164.39387312369857},
                     {'source': 'R1', 'target': 'R23', 'dist': 162.17476289756902},
                     {'source': 'R2', 'target': 'R7', 'dist': 65.13274784210944},
                     {'source': 'R2', 'target': 'R8', 'dist': 39.047970184668635},
                     {'source': 'R3', 'target': 'R10', 'dist': 32.39972641213492},
                     {'source': 'R3', 'target': 'R16', 'dist': 57.50339350652954},
                     {'source': 'R3', 'target': 'R20', 'dist': 68.74014810173368},
                     {'source': 'R4', 'target': 'R9', 'dist': 96.61494083105765},
                     {'source': 'R4', 'target': 'R13', 'dist': 79.70236028634763},
                     {'source': 'R4', 'target': 'R24', 'dist': 119.23493436665632},
                     {'source': 'R5', 'target': 'R6', 'dist': 157.67786219932535},
                     {'source': 'R5', 'target': 'R18', 'dist': 47.53697330663672},
                     {'source': 'R5', 'target': 'R22', 'dist': 113.24084877348105},
                     {'source': 'R6', 'target': 'R9', 'dist': 159.7667434356243},
                     {'source': 'R6', 'target': 'R20', 'dist': 72.92358459513315},
                     {'source': 'R6', 'target': 'R22', 'dist': 155.65931152744582},
                     {'source': 'R7', 'target': 'R8', 'dist': 59.41335447589595},
                     {'source': 'R7', 'target': 'R23', 'dist': 105.37044780763489},
                     {'source': 'R8', 'target': 'R23', 'dist': 117.87011135596511},
                     {'source': 'R9', 'target': 'R18', 'dist': 40.38342939137559},
                     {'source': 'R9', 'target': 'R24', 'dist': 138.4035842461942},
                     {'source': 'R10', 'target': 'R16', 'dist': 50.31575387682628},
                     {'source': 'R11', 'target': 'R14', 'dist': 88.74279931830297},
                     {'source': 'R11', 'target': 'R24', 'dist': 99.63853051590868},
                     {'source': 'R12', 'target': 'R15', 'dist': 51.20704462276499},
                     {'source': 'R12', 'target': 'R19', 'dist': 51.85948221105036},
                     {'source': 'R12', 'target': 'R23', 'dist': 31.437056264468467},
                     {'source': 'R12', 'target': 'R24', 'dist': 110.59520621993934},
                     {'source': 'R13', 'target': 'R17', 'dist': 74.64300656985195},
                     {'source': 'R13', 'target': 'R21', 'dist': 73.3927865101199},
                     {'source': 'R14', 'target': 'R21', 'dist': 89.663995713652},
                     {'source': 'R14', 'target': 'R24', 'dist': 75.12508380357976},
                     {'source': 'R15', 'target': 'R19', 'dist': 33.31841018550406},
                     {'source': 'R15', 'target': 'R23', 'dist': 43.73613729120682},
                     {'source': 'R16', 'target': 'R20', 'dist': 45.51511782855869},
                     {'source': 'R18', 'target': 'R19', 'dist': 35.051312753470455}]}

    for n, node in enumerate(graph['nodes']):
        assert node['id'] == org['nodes'][n]['id']
        assert node['pos'] == pytest.approx(org['nodes'][n]['pos'])

    for n, link in enumerate(graph['links']):
        assert link['source'] == org['links'][n]['source']
        assert link['target'] == org['links'][n]['target']
        assert link['dist'] == pytest.approx(org['links'][n]['dist'])

def test_save_gabriel(tmp_path):
    for s in [25, 50, 75, 100]:
        for i in [0, 1]:
            topohub.generate.GabrielGenerator.save_topo(s, (i * topohub.generate.MAX_GABRIEL_NODES) + s, filename=f'{tmp_path}/gabriel/{s}/{i}',
                                                        with_plot=True, with_topo_stats=True, with_path_stats=True)
            with (importlib.resources.files(topohub) / f'data/gabriel/{s}/{i}.json').open() as file, open(f'{tmp_path}/gabriel/{s}/{i}.json') as new_file:
                org = json.load(file)
                new = json.load(new_file)
                for key in new['graph']['stats']:
                    if key != 'avg_sdp_len':
                        assert new['graph']['stats'][key] == org['graph']['stats'][key]

                for n, node in enumerate(new['nodes']):
                    assert node['id'] == org['nodes'][n]['id']
                    assert node['pos'] == pytest.approx(org['nodes'][n]['pos'])

                for n, link in enumerate(new['links']):
                    assert link['source'] == org['links'][n]['source']
                    assert link['target'] == org['links'][n]['target']
                    assert link['dist'] == pytest.approx(org['links'][n]['dist'])
                    assert link['ecmp_fwd'] == pytest.approx(org['links'][n]['ecmp_fwd'])
                    assert link['ecmp_bwd'] == pytest.approx(org['links'][n]['ecmp_bwd'])


if __name__ == '__main__':
    test_generate_gabriel()
    test_save_gabriel('__tmp_test__')
