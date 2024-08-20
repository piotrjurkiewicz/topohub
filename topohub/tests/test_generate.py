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
           'nodes': [{'id': 0, 'name': 'R0', 'pos': (188.48115119519298, 463.3942538631604)},
                     {'id': 1, 'name': 'R1', 'pos': (421.7233695661211, 107.02288497602169)},
                     {'id': 2, 'name': 'R2', 'pos': (435.85405612271876, 318.23087287534577)},
                     {'id': 3, 'name': 'R3', 'pos': (21.19606307910038, 476.4860300622295)},
                     {'id': 4, 'name': 'R4', 'pos': (127.84183410823357, 152.950490134722)},
                     {'id': 5, 'name': 'R5', 'pos': (212.04007825311461, 294.25700701262974)},
                     {'id': 6, 'name': 'R6', 'pos': (62.1958247419368, 343.3386524356115)},
                     {'id': 7, 'name': 'R7', 'pos': (416.12026168828817, 256.1595252285978)},
                     {'id': 8, 'name': 'R8', 'pos': (397.23040888174734, 312.4899801444396)},
                     {'id': 9, 'name': 'R9', 'pos': (179.3386657302935, 234.69719113652377)},
                     {'id': 10, 'name': 'R10', 'pos': (51.992065769851045, 486.55322877152645)},
                     {'id': 11, 'name': 'R11', 'pos': (318.0147620963196, 49.1128958782206)},
                     {'id': 12, 'name': 'R12', 'pos': (291.38807712605256, 207.21298960303818)},
                     {'id': 13, 'name': 'R13', 'pos': (94.69819693315796, 80.46624667435532)},
                     {'id': 14, 'name': 'R14', 'pos': (230.37175861171588, 35.184925062400566)},
                     {'id': 15, 'name': 'R15', 'pos': (281.53890397158676, 257.46391205398623)},
                     {'id': 16, 'name': 'R16', 'pos': (63.53995848216232, 437.580570459992)},
                     {'id': 17, 'name': 'R17', 'pos': (20.26328646418918, 86.03603421640416)},
                     {'id': 18, 'name': 'R18', 'pos': (217.78065265969477, 247.06792314105613)},
                     {'id': 19, 'name': 'R19', 'pos': (252.3656251053449, 241.36930868882106)},
                     {'id': 20, 'name': 'R20', 'pos': (28.804644272073244, 408.1682618516225)},
                     {'id': 21, 'name': 'R21', 'pos': (141.4245708631205, 23.869894397222147)},
                     {'id': 22, 'name': 'R22', 'pos': (204.14203714612768, 407.22209355537865)},
                     {'id': 23, 'name': 'R23', 'pos': (314.4130966318092, 228.61712432824683)},
                     {'id': 24, 'name': 'R24', 'pos': (238.9999066946048, 109.81289084704876)}],
           'links': [{'source': 0, 'target': 16, 'dist': 127.57996663815867},
                     {'source': 0, 'target': 22, 'dist': 58.3144488305541},
                     {'source': 1, 'target': 7, 'dist': 149.2418583498508},
                     {'source': 1, 'target': 11, 'dist': 118.78148888035041},
                     {'source': 1, 'target': 12, 'dist': 164.39387312369857},
                     {'source': 1, 'target': 23, 'dist': 162.17476289756902},
                     {'source': 2, 'target': 7, 'dist': 65.13274784210944},
                     {'source': 2, 'target': 8, 'dist': 39.047970184668635},
                     {'source': 3, 'target': 10, 'dist': 32.39972641213492},
                     {'source': 3, 'target': 16, 'dist': 57.50339350652954},
                     {'source': 3, 'target': 20, 'dist': 68.74014810173368},
                     {'source': 4, 'target': 9, 'dist': 96.61494083105765},
                     {'source': 4, 'target': 13, 'dist': 79.70236028634763},
                     {'source': 4, 'target': 24, 'dist': 119.23493436665632},
                     {'source': 5, 'target': 6, 'dist': 157.67786219932535},
                     {'source': 5, 'target': 18, 'dist': 47.53697330663672},
                     {'source': 5, 'target': 22, 'dist': 113.24084877348105},
                     {'source': 6, 'target': 9, 'dist': 159.7667434356243},
                     {'source': 6, 'target': 20, 'dist': 72.92358459513315},
                     {'source': 6, 'target': 22, 'dist': 155.65931152744582},
                     {'source': 7, 'target': 8, 'dist': 59.41335447589595},
                     {'source': 7, 'target': 23, 'dist': 105.37044780763489},
                     {'source': 8, 'target': 23, 'dist': 117.87011135596511},
                     {'source': 9, 'target': 18, 'dist': 40.38342939137559},
                     {'source': 9, 'target': 24, 'dist': 138.4035842461942},
                     {'source': 10, 'target': 16, 'dist': 50.31575387682628},
                     {'source': 11, 'target': 14, 'dist': 88.74279931830297},
                     {'source': 11, 'target': 24, 'dist': 99.63853051590868},
                     {'source': 12, 'target': 15, 'dist': 51.20704462276499},
                     {'source': 12, 'target': 19, 'dist': 51.85948221105036},
                     {'source': 12, 'target': 23, 'dist': 31.437056264468467},
                     {'source': 12, 'target': 24, 'dist': 110.59520621993934},
                     {'source': 13, 'target': 17, 'dist': 74.64300656985195},
                     {'source': 13, 'target': 21, 'dist': 73.3927865101199},
                     {'source': 14, 'target': 21, 'dist': 89.663995713652},
                     {'source': 14, 'target': 24, 'dist': 75.12508380357976},
                     {'source': 15, 'target': 19, 'dist': 33.31841018550406},
                     {'source': 15, 'target': 23, 'dist': 43.73613729120682},
                     {'source': 16, 'target': 20, 'dist': 45.51511782855869},
                     {'source': 18, 'target': 19, 'dist': 35.051312753470455}]}

    for n, node in enumerate(graph['nodes']):
        assert node['id'] == org['nodes'][n]['id']
        assert node['name'] == org['nodes'][n]['name']
        assert node['pos'] == pytest.approx(org['nodes'][n]['pos'])

    for n, link in enumerate(graph['links']):
        assert link['source'] == org['links'][n]['source']
        assert link['target'] == org['links'][n]['target']
        assert link['dist'] == pytest.approx(org['links'][n]['dist'])

def test_save_gabriel(tmp_path):
    for s in [25, 50, 75, 100]:
        for i in [0, 1]:
            topohub.generate.GabrielGenerator.save_topo(s, (i * topohub.generate.MAX_GABRIEL_NODES) + s, filename=f'{tmp_path}/gabriel/{s}/{i}',
                                                        with_plot=True, with_utilization=True, with_topo_stats=True, with_path_stats=True, scale=5)
            with (importlib.resources.files(topohub) / f'data/gabriel/{s}/{i}.json').open() as file, open(f'{tmp_path}/gabriel/{s}/{i}.json') as new_file:
                org = json.load(file)
                new = json.load(new_file)
                for key in new['graph']['stats']:
                    if key != 'avg_sdp_len':
                        assert new['graph']['stats'][key] == org['graph']['stats'][key]

                for n, node in enumerate(new['nodes']):
                    assert node['id'] == org['nodes'][n]['id']
                    assert node['name'] == org['nodes'][n]['name']
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
