#!/usr/bin/python3
"""
Topo generation CLI and helpers for TopoHub.

This module orchestrates generation and saving of topologies using provider
generators. Unless otherwise noted, node positions are stored as
(longitude, latitude) tuples.
"""
import concurrent.futures
import json
import pathlib
import sys
import time

import networkx as nx

import topohub.graph

json.encoder.c_make_encoder = None

class RoundingFloat(float):
    """Float that pretty-prints with two decimal places for JSON dumps."""

    __repr__ = staticmethod(lambda x: format(x, '.2f'))

class TopoGenerator:
    """
    Base class for topology generators.

    Subclasses should implement ``generate_topo`` to return a NetworkX node-link
    format dictionary. Node positions are expected in ``pos`` as (lon, lat) tuples.
    """

    @classmethod
    def generate_topo(cls, *args, **kwargs) -> dict:
        """
        Generate a topology.

        This base implementation returns an empty node-link structure and should be
        overridden by subclasses.

        Returns
        -------
        dict
            A dictionary compatible with ``networkx.node_link_graph``.
        """
        _ = args, kwargs
        return {}

    @classmethod
    def save_topo(cls, *args, **kwargs) -> None:
        """
        Generate, post-process, and save a topology to files.

        Parameters
        ----------
        *args : tuple
            Positional arguments forwarded to ``generate_topo``.
        **kwargs : dict
            Keyword arguments forwarded to ``generate_topo`` and processing flags.
        filename : str, optional (keyword-only)
            Basename of output files (without extension). Defaults to
            ``mininet/topo_lib/<graph name>``.
        with_plot : bool, optional
            If True, save an SVG rendering of the graph.
        with_utilization : bool, optional
            If True, compute ECMP utilizations.
        with_path_stats : bool, optional
            If True, compute disjoint path statistics.
        with_topo_stats : bool, optional
            If True, compute and embed topology statistics in graph attributes.
        scale : bool | float | None, optional
            Forwarded to ``topohub.graph.save_topo_graph_svg``.
        background : list[str] | None, optional
            SVG elements for background (e.g., map paths).

        Notes
        -----
        Nodes are expected to contain ``pos`` as (lon, lat) tuples.
        """
        g = nx.node_link_graph(cls.generate_topo(*args, **kwargs), edges='edges')
        if len(g.nodes) == 0:
            print(f'Warning: generated topology {g.name} has no nodes')
            return
        if len(g.edges) == 0:
            print(f'Warning: generated topology {g.name} has no edges')
            return
        filename = kwargs.get('filename', f'mininet/topo_lib/{g.name}')
        pathlib.Path(filename).parent.mkdir(parents=True, exist_ok=True)
        ps = None
        if kwargs.get('with_plot'):
            topohub.graph.save_topo_graph_svg(g, filename, kwargs.get('scale'), kwargs.get('background'))
        if kwargs.get('with_utilization'):
            topohub.graph.calculate_utilization(g, node_filter=kwargs.get('node_filter'))
        if kwargs.get('with_path_stats'):
            ps = topohub.graph.path_stats(g, node_filter=kwargs.get('node_filter'))
            topohub.graph.path_stats_print(ps, filename)
        if kwargs.get('with_topo_stats'):
            ts = topohub.graph.topo_stats(g, ps)
            # graph.topo_stats_print(ts, g.graph['name'], filename)
            g.graph['stats'] = ts
        json.encoder.float = RoundingFloat
        json.dump(nx.node_link_data(g, edges='edges'), open(f'{filename}.json', 'w'), indent=kwargs.get('indent', 0), default=lambda x: format(x, '.2f'))
        json.encoder.float = float
        topohub.graph.write_gml(g, f'{filename}.gml')

def main(topo_names):
    """
    CLI entry point to generate and save multiple topology sets.

    Parameters
    ----------
    topo_names : list[str]
        A list whose first element selects the provider/group, e.g., 'gabriel',
        'sndlib', 'topozoo', 'backbone', 'caida'. Remaining behavior is
        specialized per provider in this function body.
    """

    if topo_names[0] == 'gabriel':

        import topohub.providers.gabriel

        gen = topohub.providers.gabriel.GabrielGenerator
        max_gabriel_nodes = topohub.providers.gabriel.MAX_GABRIEL_NODES

        for nodes_number in range(25, 525, 25):
            start_time = time.time()
            for i in range(10):
                gen.save_topo(nodes_number, (i * max_gabriel_nodes) + nodes_number, filename=f'data/gabriel/{nodes_number}/{i}', with_plot=True, with_utilization=True, with_topo_stats=True, with_path_stats=True, scale=5)
            print(time.time() - start_time)

    elif topo_names[0] == 'sndlib':

        import topohub.providers.sndlib
        import topohub.geo

        gen = topohub.providers.sndlib.SNDlibGenerator

        topo_names = {
            'abilene': {'include_countries': ['US']},
            'atlanta': None,
            'brain': {'include_countries': ['Germany']},
            'cost266': {'include_continents': ['EU']},
            'dfn-bwin': {'include_countries': ['Germany']},
            'dfn-gwin': {'include_countries': ['Germany']},
            'di-yuan': None,
            'france': None,
            'geant': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'germany50': {'include_countries': ['Germany']},
            'giul39': None,
            'india35': None,
            'janos-us': {'include_countries': ['US']},
            'janos-us-ca': {'include_countries': ['US', 'Canada']},
            'newyork': None,
            'nobel-eu': {'include_continents': ['EU']},
            'nobel-germany': {'include_countries': ['Germany']},
            'nobel-us': {'include_countries': ['US']},
            'norway': None,
            'pdh': {'include_countries': ['Germany']},
            'pioro40': None,
            'polska': {'include_countries': ['Poland']},
            'sun': None,
            'ta1': None,
            'ta2': None,
            'zib54': None,
        }

        for topo_name in topo_names:
            if topo_names[topo_name]:
                background = topohub.geo.generate_map(**topo_names[topo_name])
            else:
                background = None
            gen.save_topo(topo_name, filename=f'data/sndlib/{topo_name}', with_plot=True, with_utilization=True, with_path_stats=True, with_topo_stats=True, background=background, scale=True)

    elif topo_names[0] == 'topozoo':

        import topohub.providers.topozoo
        import topohub.geo

        gen = topohub.providers.topozoo.TopoZooGenerator

        topo_names = {
            'Aarnet': {'include_countries': ['Australia']},
            'Abilene': {'include_countries': ['US']},
            'Abvt': {'include_continents': ['EU'], 'include_countries': ['US', 'Japan']},
            'Aconet': {'include_countries': ['Austria']},
            'Agis': {'include_countries': ['US']},
            'Airtel': {'include_continents': ['EU', 'Asia'], 'include_countries': ['US']},
            # 'Ai3': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Amres': {'include_countries': ['Serbia']},
            'Ans': {'include_countries': ['United States of America']},
            'Arn': {'include_countries': ['Algeria']},
            'Arnes': {'include_countries': ['Slovenia']},
            'Arpanet196912': {'include_countries': ['US']},
            'Arpanet19706': {'include_countries': ['US']},
            'Arpanet19719': {'include_countries': ['US']},
            'Arpanet19723': {'include_countries': ['US']},
            'Arpanet19728': {'include_countries': ['US']},
            'AsnetAm': {'include_countries': ['US']},
            'Atmnet': {'include_countries': ['US']},
            'AttMpls': {'include_countries': ['US']},
            # 'Azrena': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Bandcon': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Basnet': {'include_countries': ['Belarus']},
            'Bbnplanet': {'include_countries': ['US']},
            'Bellcanada': {'include_countries': ['US', 'Canada']},
            'Bellsouth': {'include_countries': ['US']},
            'Belnet2003': {'include_countries': ['Belgium']},
            'Belnet2004': {'include_countries': ['Belgium']},
            'Belnet2005': {'include_countries': ['Belgium']},
            'Belnet2006': {'include_countries': ['Belgium']},
            'Belnet2007': {'include_countries': ['Belgium']},
            'Belnet2008': {'include_countries': ['Belgium']},
            'Belnet2009': {'include_countries': ['Belgium']},
            'Belnet2010': {'include_countries': ['Belgium']},
            'BeyondTheNetwork': {'include_countries': ['US']},
            'Bics': {'include_continents': ['EU']},
            'Biznet': {'include_countries': ['Indonesia']},
            # 'Bren': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'BsonetEurope': {'include_continents': ['EU']},
            'BtAsiaPac': {'include_continents': ['Asia', 'Oceania']},
            'BtEurope': {'include_continents': ['EU']},
            # 'BtLatinAmerica': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'BtNorthAmerica': {'include_countries': ['US']},
            'Canerie': {'include_countries': ['US', 'Canada']},
            'Carnet': {'include_countries': ['Croatia']},
            'Cernet': {'include_countries': ['China']},
            'Cesnet1993': {'include_countries': ['Czechia']},
            'Cesnet1997': {'include_countries': ['Czechia']},
            'Cesnet1999': {'include_countries': ['Czechia']},
            'Cesnet2001': {'include_countries': ['Czechia']},
            'Cesnet200304': {'include_countries': ['Czechia']},
            'Cesnet200511': {'include_countries': ['Czechia']},
            'Cesnet200603': {'include_countries': ['Czechia']},
            'Cesnet200706': {'include_countries': ['Czechia']},
            'Cesnet201006': {'include_countries': ['Czechia']},
            'Chinanet': {'include_countries': ['China']},
            'Claranet': {'include_continents': ['EU']},
            # 'Cogentco': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Colt': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Columbus': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Compuserve': {'include_countries': ['US']},
            'CrlNetworkServices': {'include_countries': ['US']},
            # 'Cudi': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Cwix': {'include_countries': ['US']},
            'Cynet': {'include_countries': ['Cyprus']},
            'Darkstrand': {'include_countries': ['US']},
            'Dataxchange': {'include_countries': ['US']},
            # 'Deltacom': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'DeutscheTelekom': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Dfn': {'include_countries': ['Germany']},
            # 'DialtelecomCz': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Digex': {'include_countries': ['US']},
            # 'Easynet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Eenet': {'include_countries': ['Estonia']},
            'EliBackbone': {'include_countries': ['US']},
            'Epoch': {'include_countries': ['US']},
            'Ernet': {'include_countries': ['India']},
            # 'Esnet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Eunetworks': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Evolink': {'include_countries': ['Bulgaria']},
            # 'Fatman': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Fccn': {'include_countries': ['Portugal']},
            'Forthnet': {'include_countries': ['Greece']},
            'Funet': {'include_countries': ['Finland']},
            'Gambia': {'include_countries': ['Gambia']},
            'Garr199901': {'include_countries': ['Italy']},
            'Garr199904': {'include_countries': ['Italy']},
            'Garr199905': {'include_countries': ['Italy']},
            'Garr200109': {'include_countries': ['Italy']},
            'Garr200112': {'include_countries': ['Italy']},
            'Garr200212': {'include_countries': ['Italy']},
            'Garr200404': {'include_countries': ['Italy']},
            'Garr200902': {'include_countries': ['Italy']},
            'Garr200908': {'include_countries': ['Italy']},
            'Garr200909': {'include_countries': ['Italy']},
            'Garr200912': {'include_countries': ['Italy']},
            'Garr201001': {'include_countries': ['Italy']},
            'Garr201003': {'include_countries': ['Italy']},
            'Garr201004': {'include_countries': ['Italy']},
            'Garr201005': {'include_countries': ['Italy']},
            'Garr201007': {'include_countries': ['Italy']},
            'Garr201008': {'include_countries': ['Italy']},
            'Garr201010': {'include_countries': ['Italy']},
            'Garr201012': {'include_countries': ['Italy']},
            'Garr201101': {'include_countries': ['Italy']},
            'Garr201102': {'include_countries': ['Italy']},
            'Garr201103': {'include_countries': ['Italy']},
            'Garr201104': {'include_countries': ['Italy']},
            'Garr201105': {'include_countries': ['Italy']},
            'Garr201107': {'include_countries': ['Italy']},
            'Garr201108': {'include_countries': ['Italy']},
            'Garr201109': {'include_countries': ['Italy']},
            'Garr201110': {'include_countries': ['Italy']},
            'Garr201111': {'include_countries': ['Italy']},
            'Garr201112': {'include_countries': ['Italy']},
            'Garr201201': {'include_countries': ['Italy']},
            'Gblnet': {'include_continents': ['EU']},
            'Geant2001': {'include_continents': ['EU'], 'include_countries': ['Israel', 'Cyprus']},
            'Geant2009': {'include_continents': ['EU'], 'include_countries': ['Israel', 'Turkey', 'Cyprus']},
            'Geant2010': {'include_continents': ['EU'], 'include_countries': ['Israel', 'Turkey', 'Cyprus']},
            'Geant2012': {'include_continents': ['EU'], 'include_countries': ['Israel', 'Turkey', 'Cyprus']},
            'Getnet': {'include_countries': ['US']},
            'Globalcenter': {'include_countries': ['US']},
            # 'Globenet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Goodnet': {'include_countries': ['US']},
            'Grena': {'include_countries': ['Georgia']},
            'Gridnet': {'include_countries': ['US']},
            'Grnet': {'include_countries': ['Greece']},
            # 'GtsCe': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'GtsCzechRepublic': {'include_countries': ['Czechia']},
            'GtsHungary': {'include_countries': ['Hungary']},
            'GtsPoland': {'include_countries': ['Poland']},
            'GtsRomania': {'include_countries': ['Romania']},
            'GtsSlovakia': {'include_countries': ['Slovakia']},
            # 'Harnet': {'include_countries': ['Ireland']},
            'Heanet': {'include_countries': ['Ireland']},
            'HiberniaCanada': {'include_countries': ['Canada']},
            'HiberniaGlobal': {'include_continents': ['EU'], 'include_countries': ['US']},
            'HiberniaIreland': {'include_countries': ['Ireland']},
            'HiberniaNireland': {'include_countries': ['Ireland', 'United Kingdom']},
            'HiberniaUk': {'include_countries': ['United Kingdom']},
            'HiberniaUs': {'include_countries': ['US', 'Canada']},
            'Highwinds': {'include_continents': ['North America', 'South America', 'Europe'], 'exclude_countries': ['Russia']},
            'HostwayInternational': {'include_continents': ['all']},
            'HurricaneElectric': {'include_continents': ['all']},
            'Ibm': {'include_countries': ['US']},
            'Iij': {'include_countries': ['US', 'Japan']},
            'Iinet': {'include_countries': ['Australia']},
            'Ilan': {'include_countries': ['Israel']},
            'Integra': {'include_countries': ['US']},
            # 'Intellifiber': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Internetmci': {'include_countries': ['US']},
            'Internode': {'include_continents': ['all']},
            # 'Interoute': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Intranetwork': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Ion': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'IowaStatewideFiberMap': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Iris': {'include_countries': ['US']},
            'Istar': {'include_countries': ['Canada']},
            'Itnet': {'include_countries': ['Ireland']},
            'Janetbackbone': {'include_countries': ['United Kingdom']},
            # 'JanetExternal': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Janetlense': {'include_countries': ['United Kingdom']},
            'Jgn2Plus': {'include_countries': ['Japan']},
            'Karen': {'include_countries': ['New Zealand']},
            # 'Kdl': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'KentmanApr2007': {'include_countries': ['United Kingdom']},
            # 'KentmanAug2005': {'include_countries': ['United Kingdom']},
            'KentmanFeb2008': {'include_countries': ['United Kingdom']},
            # 'KentmanJan2011': {'include_countries': ['United Kingdom']},
            'KentmanJul2005': {'include_countries': ['United Kingdom']},
            'Kreonet': {'include_countries': ['South Korea']},
            # 'LambdaNet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Latnet': {'include_countries': ['Latvia']},
            'Layer42': {'include_countries': ['US']},
            'Litnet': {'include_countries': ['Lithuania']},
            'Marnet': {'include_countries': ['North Macedonia']},
            'Marwan': {'include_countries': ['Morocco']},
            # 'Missouri': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Mren': {'include_countries': ['Montenegro']},
            'Myren': {'include_countries': ['Malaysia']},
            'Napnet': {'include_countries': ['US']},
            'Navigata': {'include_countries': ['Canada']},
            'Netrail': {'include_countries': ['US']},
            'NetworkUsa': {'include_countries': ['US']},
            'Nextgen': {'include_countries': ['Australia']},
            'Niif': {'include_countries': ['Hungary']},
            'Noel': {'include_countries': ['US', 'Canada']},
            'Nordu1989': {'include_continents': ['EU']},
            'Nordu1997': {'include_continents': ['EU']},
            'Nordu2005': {'include_continents': ['EU']},
            # 'Nordu2010': {'include_continents': ['EU']},
            # 'Nsfcnet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Nsfnet': {'include_countries': ['US']},
            # 'Ntelos': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Ntt': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Oteglobe': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Oxford': {'include_countries': ['US']},
            'Pacificwave': {'include_countries': ['US']},
            'Packetexchange': {'include_continents': ['all']},
            # 'Padi': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Palmetto': {'include_countries': ['US']},
            'Peer1': {'include_continents': ['North America', 'Europe'], 'exclude_countries': ['Russia']},
            # 'Pern': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'PionierL1': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'PionierL3': {'include_countries': ['Poland']},
            'Psinet': {'include_countries': ['US']},
            'Quest': {'include_continents': ['all']},
            # 'RedBestel': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Rediris': {'include_countries': ['Spain']},
            'Renam': {'include_countries': ['Moldova']},
            'Renater1999': {'include_countries': ['France']},
            'Renater2001': {'include_countries': ['France']},
            'Renater2004': {'include_countries': ['France']},
            'Renater2006': {'include_countries': ['France']},
            'Renater2008': {'include_countries': ['France']},
            'Renater2010': {'include_countries': ['France']},
            'Restena': {'include_countries': ['Luxembourg']},
            # 'Reuna': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Rhnet': {'include_countries': ['Iceland']},
            'Rnp': {'include_countries': ['Brazil']},
            'Roedunet': {'include_countries': ['Romania']},
            # 'RoedunetFibre': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Sago': {'include_countries': ['US']},
            # 'Sanet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Sanren': {'include_countries': ['South Africa']},
            'Savvis': {'include_countries': ['US']},
            # 'Shentel': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Sinet': {'include_countries': ['Japan']},
            # 'Singaren': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Spiralight': {'include_countries': ['US']},
            'Sprint': {'include_countries': ['US']},
            'Sunet': {'include_countries': ['Sweden']},
            'Surfnet': {'include_countries': ['Kingdom of the Netherlands']},
            # 'Switch': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'SwitchL3': {'include_countries': ['Switzerland']},
            # 'Syringa': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'TataNld': {'include_countries': ['India']},
            # 'Telcove': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Telecomserbia': {'include_countries': ['Serbia', 'Montenegro']},
            # 'Tinet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'TLex': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Tw': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'Twaren': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Ulaknet': {'include_countries': ['Turkey']},
            'UniC': {'include_countries': ['Denmark']},
            # 'Uninet': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Uninett2010': {'include_countries': ['Norway']},
            'Uninett2011': {'include_countries': ['Norway', 'Sweden']},
            'Uran': {'include_countries': ['Ukraine']},
            # 'UsCarrier': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            # 'UsSignal': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']},
            'Uunet': {'include_countries': ['US', 'Canada']},
            'Vinaren': {'include_continents': ['Asia', 'Oceania']},
            'VisionNet': {'include_countries': ['US']},
            'VtlWavenet2008': {'include_continents': ['EU']},
            'VtlWavenet2011': {'include_continents': ['EU']},
            'WideJpn': {'include_continents': ['all']},
            'Xeex': {'include_continents': ['all']},
            'Xspedius': {'include_countries': ['US']},
            'York': {'include_countries': ['United Kingdom']},
            # 'Zamren': {'include_continents': ['EU'], 'include_countries': ['US', 'Israel']}
        }

        for topo_name in topo_names:
            print(topo_name)
            if topo_names[topo_name]:
                background = topohub.geo.generate_map(**topo_names[topo_name])
            else:
                background = None
            try:
                gen.save_topo(topo_name, filename=f'data/topozoo/{topo_name}', with_plot=True, with_utilization=True, with_path_stats=True, with_topo_stats=True, background=background, scale=True)
            except nx.exception.NetworkXNoPath:
                pass
            except nx.NetworkXError:
                pass
            except ValueError as exc:
                if exc.args[0] == 'Empty graph':
                    pass
                else:
                    raise

    elif topo_names[0] == 'backbone':

        import topohub.providers.backbone
        import topohub.geo

        gen = topohub.providers.backbone.BackboneGenerator

        topo_names = {
            'africa': {'include_continents': ['Africa']},
            'africa_nosc': {'include_continents': ['Africa']},
            'americas': {'include_continents': ['North America', 'South America']},
            'americas_nosc': {'include_continents': ['North America', 'South America']},
            'atlantica': {'include_continents': ['North America', 'Europe'], 'include_countries': ['Turkey', 'Georgia', 'Cyprus'], 'exclude_countries': ['Russia']},
            'eastern': {'include_continents': ['Europe', 'Africa', 'Asia', 'Oceania']},
            'eastern_nosc': {'include_continents': ['Europe', 'Africa', 'Asia', 'Oceania']},
            'emea': {'include_continents': ['Europe', 'Africa', 'Asia']},
            'emea_nosc': {'include_continents': ['Europe', 'Africa', 'Asia']},
            'eurafrasia': {'include_continents': ['Europe', 'Africa', 'Asia']},
            'eurafrasia_nosc': {'include_continents': ['Europe', 'Africa', 'Asia']},
            'eurasia': {'include_continents': ['Europe', 'Asia']},
            'eurasia_nosc': {'include_continents': ['Europe', 'Asia']},
            'europe': {'include_continents': ['Europe'], 'include_countries': ['Turkey', 'Georgia', 'Cyprus'], 'exclude_countries': ['Russia']},
            'europe_nosc': {'include_continents': ['Europe'], 'include_countries': ['Turkey', 'Georgia', 'Cyprus'], 'exclude_countries': ['Russia']},
            'north_america': {'include_continents': ['North America']},
            'north_america_nosc': {'include_continents': ['North America']},
            'south_america': {'include_continents': ['South America']},
            'south_america_nosc': {'include_continents': ['South America']},
            'world': {'include_continents': ['all']},
        }

        for topo_name in topo_names:
            background = []
            if topo_names[topo_name]:
                background = topohub.geo.generate_map(**topo_names[topo_name])
            # region = topohub.backbone.regions.get(topo_name)
            # if topo_name.endswith('_nosc'):
            #     region = topohub.backbone.regions.get(topo_name[:-5])
            # if region:
            #     path_data = topohub.backbone.polygon_to_path(region)
            #     background.append(f'<path class="selection" vector-effect="non-scaling-stroke" d="{path_data}"/>\n')
            gen.save_topo(topo_name, filename=f'data/backbone/{topo_name}', with_plot=True, with_utilization=True, with_path_stats=True, with_topo_stats=True, background=background, scale=0.1, node_filter=lambda n: n['type'] == 'City')

    elif topo_names[0] == 'caida':

        import topohub.providers.caida
        import topohub.geo

        gen = topohub.providers.caida.CaidaGenerator

        topo_names = {
            # NRENs (research and education networks)
            # '11537': {'distance_km': 25, 'include_countries': ['United States'], 'mainland_only': False},              # Internet2 (US)
            # '1237':  {'distance_km': 25, 'include_continents': ['Asia'], 'mainland_only': False},                      # KREONET
            # '12687': {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': False},                        # URAN
            # '13010': {'distance_km': 25, 'include_countries': ['Serbia'], 'mainland_only': False},                     # AMRES (RS)
            # '15474': {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': False},                        # RHnet
            # '17579': {'distance_km': 25, 'include_countries': ['South Korea'], 'mainland_only': False},                # KREONET (KR)
            # '1850':  {'distance_km': 25, 'include_countries': ['Iceland'], 'mainland_only': False},                    # RHnet (IS)
            # '201814':{'distance_km': 25, 'include_countries': ['Lithuania'], 'mainland_only': False},                  # LITNET (LT)
            # '20545': {'distance_km': 25, 'include_continents': ['Europe'], 'mainland_only': False},                    # GRENA
            # '2108':  {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': False},                        # CARNET
            # '24514': {'distance_km': 25, 'include_countries': ['Malaysia'], 'mainland_only': False},                   # MYREN (MY)
            # '2602':  {'distance_km': 25, 'include_countries': ['Luxembourg'], 'mainland_only': False},                 # RESTENA
            # '30983': {'distance_km': 25, 'include_countries': ['Morocco'], 'mainland_only': False},                    # MARWAN (MA)
            # '327687':{'distance_km': 25, 'include_countries': ['Uganda'], 'mainland_only': False},                     # RENU (UG)
            # '327700':{'distance_km': 25, 'include_countries': ['Mozambique'], 'mainland_only': False},                 # MoRENet (MZ)
            # '3661':  {'distance_km': 25, 'include_countries': ['Hong Kong'], 'mainland_only': False},                  # HARNET (HK)
            # '3662':  {'distance_km': 25, 'include_countries': ['Hong Kong'], 'mainland_only': False},                  # HARNET (HK)
            # '36914': {'distance_km': 25, 'include_countries': ['Kenya'], 'mainland_only': False},                      # KENET (KE)
            # '36944': {'distance_km': 25, 'include_countries': ['Tanzania'], 'mainland_only': False},                   # TERNET (TZ)
            # '37180': {'distance_km': 25, 'include_countries': ['South Africa'], 'mainland_only': False},               # SANReN/TENET edge (ZA)
            # '37182': {'distance_km': 25, 'include_countries': ['Tanzania'], 'mainland_only': False},                   # TERNET (TZ)
            # '37233': {'distance_km': 25, 'include_countries': ['Uganda'], 'mainland_only': False},                     # RENU (UG)
            # '378':   {'distance_km': 25, 'include_countries': ['Israel'], 'mainland_only': False},                     # IUCC (ILAN)
            # '38229': {'distance_km': 25, 'include_countries': ['Sri Lanka'], 'mainland_only': False},                  # LEARN (LK)
            # '44224': {'distance_km': 25, 'include_countries': ['North Macedonia'], 'mainland_only': False},            # MARNET
            # '4651':  {'distance_km': 25, 'include_countries': ['Thailand'], 'mainland_only': False},                   # UniNet (TH)
            # '5504':  {'distance_km': 25, 'include_countries': ['Cyprus'], 'mainland_only': False},                     # CYNET (CY)
            # '5539':  {'distance_km': 25, 'include_countries': ['Latvia'], 'mainland_only': False},                     # SigmaNet (LV)
            # '55824': {'distance_km': 25, 'include_countries': ['India'], 'mainland_only': False},                      # NKN (IN)
            # '55847': {'distance_km': 25, 'include_countries': ['India'], 'mainland_only': False},                      # NKN Edge (IN)
            # '61468': {'distance_km': 25, 'include_countries': ['Ecuador'], 'mainland_only': False},                    # CEDIA (EC)
            # '6509':  {'distance_km': 25, 'include_countries': ['Canada'], 'mainland_only': False},                     # CANARIE
            # '8501':  {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': False},                        # PIONIER
            # '8517':  {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': False},                        # ULAKNET
            # '9112':  {'distance_km': 25, 'include_countries': ['Poland'], 'mainland_only': False},                     # PIONIER/PSNC (PL)
            # '9199':  {'distance_km': 25, 'include_countries': ['Moldova'], 'mainland_only': False},                    # RENAM
            # '9394':  {'distance_km': 25, 'include_countries': ['Singapore'], 'mainland_only': False},                  # SingAREN (SG)
            '1103':  {'distance_km': 25, 'include_countries': ['Netherlands'], 'mainland_only': False},                  # SURF
            '11340': {'distance_km': 25, 'include_countries': ['Chile'], 'mainland_only': False},                        # REUNA (CL)
            '1213':  {'distance_km': 25, 'include_countries': ['Ireland'], 'mainland_only': False},                      # HEAnet
            '13092': {'distance_km': 25, 'include_countries': ['Serbia'], 'mainland_only': False},                       # AMRES
            '136968':{'distance_km': 25, 'include_countries': ['Singapore'], 'mainland_only': False},                    # SingAREN (SG)
            '137':   {'distance_km': 25, 'include_countries': ['Italy'], 'mainland_only': False},                        # GARR
            '1653':  {'distance_km': 25, 'include_countries': ['Sweden'], 'mainland_only': False},                       # SUNET
            '1659':  {'distance_km': 25, 'include_countries': ['Taiwan'], 'mainland_only': False},                       # TANet/TWAREN (TW)
            '1741':  {'distance_km': 25, 'include_countries': ['Finland'], 'mainland_only': False},                      # FUNET
            '17557': {'distance_km': 25, 'include_countries': ['Pakistan'], 'mainland_only': False},                     # PERN (PK)
            '1835':  {'distance_km': 25, 'include_countries': ['Denmark'], 'mainland_only': False},                      # DeiC/Forskningsnet (DK)
            '1853':  {'distance_km': 25, 'include_countries': ['Austria'], 'mainland_only': False},                      # ACOnet
            '1916':  {'distance_km': 25, 'include_countries': ['Brazil'], 'mainland_only': False},                       # RNP (Brazil)
            '1930':  {'distance_km': 25, 'include_countries': ['Portugal'], 'mainland_only': False},                     # RCTS/FCCN
            '1955':  {'distance_km': 25, 'include_countries': ['Hungary'], 'mainland_only': False},                      # KIFÜ/HUNGARNET
            '2018':  {'distance_km': 25, 'include_countries': ['South Africa'], 'mainland_only': False},                 # TENET/SANReN
            '20965': {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': False},                          # GÉANT
            '2107':  {'distance_km': 25, 'include_countries': ['Slovenia'], 'mainland_only': False},                     # ARNES
            '211779':{'distance_km': 25, 'include_countries': ['Cyprus'], 'mainland_only': False},                       # CYNET
            '2152':  {'distance_km': 25, 'include_countries': ['US'], 'mainland_only': False},                           # CENIC (CalREN)
            '2200':  {'distance_km': 25, 'include_countries': ['France'], 'mainland_only': False},                       # RENATER
            '224':   {'distance_km': 25, 'include_countries': ['Norway'], 'mainland_only': False},                       # UNINETT/SIKT
            '2603':  {'distance_km': 25, 'include_countries': ['Denmark', 'Finland', 'Iceland', 'Norway', 'Sweden']},    # NORDUnet
            '2607':  {'distance_km': 25, 'include_countries': ['Slovakia'], 'mainland_only': False},                     # SANET
            '2611':  {'distance_km': 25, 'include_countries': ['Belgium'], 'mainland_only': False},                      # BELNET
            '2614':  {'distance_km': 25, 'include_countries': ['Romania'], 'mainland_only': False},                      # RoEduNet
            '27750': {'distance_km': 25, 'include_countries': ['Uruguay', 'Chile', 'Argentina', 'Brazil', 'Colombia'], 'mainland_only': False},  # RedCLARA (regional)
            '2847':  {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': False},                          # LITNET
            '2852':  {'distance_km': 25, 'include_countries': ['Czechia'], 'mainland_only': False},                      # CESNET
            '2907':  {'distance_km': 25, 'include_countries': ['Japan'], 'mainland_only': False},                        # SINET
            '293':   {'distance_km': 25, 'include_countries': ['US'], 'mainland_only': False},                           # ESnet
            '3221':  {'distance_km': 25, 'include_countries': ['Estonia'], 'mainland_only': False},                      # EENet
            '38022': {'distance_km': 25, 'include_countries': ['New Zealand'], 'mainland_only': False},                  # REANNZ
            '4538':  {'distance_km': 25, 'include_countries': ['China'], 'mainland_only': False},                        # CERNET
            '4771':  {'distance_km': 25, 'include_countries': ['New Zealand'], 'mainland_only': False},                  # Spark
            '50006': {'distance_km': 25, 'include_countries': ['Belarus'], 'mainland_only': False},                      # BASNET (BY)
            '5384':  {'distance_km': 25, 'include_countries': ['United Arab Emirates'], 'mainland_only': False},         # Ankabut (AE)
            '5408':  {'distance_km': 25, 'include_countries': ['Greece'], 'mainland_only': False},                       # GRNET
            '559':   {'distance_km': 25, 'include_countries': ['Switzerland'], 'mainland_only': False},                  # SWITCH
            '680':   {'distance_km': 25, 'include_countries': ['Germany'], 'mainland_only': False},                      # DFN
            '7497':  {'distance_km': 25, 'include_countries': ['China'], 'mainland_only': False},                        # CSTNET (CN)
            '7575':  {'distance_km': 25, 'include_countries': ['Australia'], 'mainland_only': False},                    # AARNet
            '766':   {'distance_km': 25, 'include_countries': ['Spain'], 'mainland_only': False},                        # RedIRIS
            '786':   {'distance_km': 25, 'include_countries': ['United Kingdom'], 'mainland_only': False},               # JANET

            # Operators (national/regional providers)
            # '12338': {'distance_km': 25, 'include_countries': ['Norway'], 'mainland_only': False},                     # Telenor Norge
            # '1241':  {'distance_km': 25, 'include_countries': ['Denmark'], 'mainland_only': False},                    # TDC (DK)
            # '12578': {'distance_km': 25, 'include_countries': ['Poland'], 'mainland_only': False},                     # Polkomtel (Plus)
            # '13127': {'distance_km': 25, 'include_countries': ['Austria'], 'mainland_only': False},                    # A1 Telekom Austria
            # '15895': {'distance_km': 25, 'include_countries': ['Türkiye'], 'mainland_only': False},                    # Turkcell Superonline
            # '2116':  {'distance_km': 25, 'include_countries': ['Denmark'], 'mainland_only': False},                    # GlobalConnect (Nordic)
            # '3243':  {'distance_km': 25, 'include_countries': ['Hungary'], 'mainland_only': False},                    # DIGI Hungary
            # '3267':  {'distance_km': 25, 'include_countries': ['Russia'], 'mainland_only': False},                     # MF/RTC (regional)
            # '33764': {'distance_km': 25, 'include_countries': ['Ghana'], 'mainland_only': False},                      # Vodafone Ghana
            # '35320': {'distance_km': 25, 'include_countries': ['Hungary'], 'mainland_only': False},                    # DIGI Távközlési
            # '37100': {'distance_km': 25, 'include_countries': ['Kenya'], 'mainland_only': False},                      # Safaricom (KE)
            # '4713':  {'distance_km': 25, 'include_countries': ['France'], 'mainland_only': False},                     # NTT
            # '4809':  {'distance_km': 25, 'include_countries': ['China'], 'mainland_only': False},                      # China Mobile CMNET (CN)
            # '5378':  {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': False},                        # Vodafone UK
            # '5603':  {'distance_km': 25, 'include_countries': ['Slovenia'], 'mainland_only': False},                   # Telekom Slovenije
            # '56038': {'distance_km': 25, 'include_countries': ['India'], 'mainland_only': False},                      # Jio (IN, national)
            # '56054': {'distance_km': 25, 'include_countries': ['Nigeria'], 'mainland_only': False},                    # MTN Nigeria
            # '6667':  {'distance_km': 25, 'include_countries': ['Finland'], 'mainland_only': False},                    # Elisa FI
            # '6848':  {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': False},                        # Telenet BE
            # '8422':  {'distance_km': 25, 'include_countries': ['Germany'], 'mainland_only': False},                    # NetCologne
            # '8426':  {'distance_km': 25, 'include_countries': ['Portugal'], 'mainland_only': False},                   # NOS
            # '8551':  {'distance_km': 25, 'include_countries': ['Israel'], 'mainland_only': False},                     # Partner
            # '9044':  {'distance_km': 25, 'include_countries': ['Ukraine'], 'mainland_only': False},                    # Kyivstar
            # '9121':  {'distance_km': 25, 'include_countries': ['Türkiye'], 'mainland_only': False},                    # Türk Telekom
            # '9198':  {'distance_km': 25, 'include_countries': ['Israel'], 'mainland_only': False},                     # Bezeq
            '1136':  {'distance_km': 25, 'include_countries': ['Netherlands'], 'mainland_only': False},                  # KPN NL
            '1221':  {'distance_km': 50, 'include_countries': ['Australia'], 'mainland_only': False},                    # Telstra (AU)
            '12322': {'distance_km': 25, 'include_countries': ['France'], 'mainland_only': False},                       # Free SAS (Iliad)
            '12479': {'distance_km': 25, 'include_countries': ['Spain'], 'mainland_only': False},                        # Orange Spain (ES)
            '1257':  {'distance_km': 25, 'include_countries': ['Sweden'], 'mainland_only': False},                       # Tele2 SE
            '12741': {'distance_km': 25, 'include_countries': ['Poland'], 'mainland_only': False},                       # Netia
            '12874': {'distance_km': 25, 'include_countries': ['Italy'], 'mainland_only': False},                        # Fastweb (IT)
            '12912': {'distance_km': 25, 'include_countries': ['Poland'], 'mainland_only': False},                       # T-Mobile Polska
            '15525': {'distance_km': 25, 'include_countries': ['Portugal'], 'mainland_only': True},                      # MEO (PT)
            '15895': {'distance_km': 25, 'include_countries': ['Turkey'], 'mainland_only': False},                       # Turkcell Superonline (TR)
            '16086': {'distance_km': 25, 'include_countries': ['Finland'], 'mainland_only': False},                      # DNA (FI)
            '20115': {'distance_km': 25, 'include_countries': ['US'], 'mainland_only': False},                           # Charter (Spectrum)
            '2119':  {'distance_km': 25, 'include_countries': ['Norway'], 'mainland_only': False},                       # Telenor NO
            '21928': {'distance_km': 25, 'include_countries': ['Czechia'], 'mainland_only': False},                      # O2 Czechia (retail)
            '2856':  {'distance_km': 25, 'include_countries': ['United Kingdom'], 'mainland_only': False},               # BT UK
            '2905':  {'distance_km': 25, 'include_countries': ['United Kingdom'], 'mainland_only': False},               # The Phone Co-op/Plusnet UK
            '29562': {'distance_km': 25, 'include_countries': ['Germany'], 'mainland_only': False},                      # Vodafone Kabel Deutschland
            '3209':  {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': False},                          # Vodafone DE
            '3215':  {'distance_km': 25, 'include_countries': ['France'], 'mainland_only': True},                        # Orange France
            '3269':  {'distance_km': 25, 'include_countries': ['Italy'], 'mainland_only': False},                        # TIM Italia
            '3292':  {'distance_km': 25, 'include_countries': ['Denmark'], 'mainland_only': False},                      # TDC DK
            '3301':  {'distance_km': 25, 'include_countries': ['Sweden'], 'mainland_only': False},                       # Telia Sweden (domestic)
            '3303':  {'distance_km': 25, 'include_countries': ['Switzerland'], 'mainland_only': False},                  # Swisscom
            '3320':  {'distance_km': 25, 'include_countries': ['Germany'], 'mainland_only': False},                      # Deutsche Telekom
            '3329':  {'distance_km': 25, 'include_countries': ['Greece'], 'mainland_only': False},                       # Cosmote (GR)
            '3352':  {'distance_km': 25, 'include_countries': ['Spain'], 'mainland_only': False},                        # Telefónica Spain
            '3356':  {'distance_km': 25, 'include_countries': ['US'], 'mainland_only': False},                           # Lumen / Level(3)
            '3741':  {'distance_km': 25, 'include_countries': ['South Africa'], 'mainland_only': False},                 # Telkom SA
            '39651': {'distance_km': 25, 'include_countries': ['Sweden'], 'mainland_only': False},                       # Com Hem (SE)
            '4134':  {'distance_km': 25, 'include_countries': ['China'], 'mainland_only': False},                        # China Telecom (CN)
            '4739':  {'distance_km': 50, 'include_countries': ['Australia'], 'mainland_only': False},                    # Optus (AU)
            '4766':  {'distance_km': 25, 'include_countries': ['South Korea'], 'mainland_only': False},                  # Korea Telecom (KR)
            '4837':  {'distance_km': 25, 'include_countries': ['China'], 'mainland_only': False},                        # China Unicom (CN)
            '5089':  {'distance_km': 25, 'include_countries': ['United Kingdom'], 'mainland_only': False},               # Virgin Media UK
            '5410':  {'distance_km': 25, 'include_countries': ['France'], 'mainland_only': False},                       # Bouygues Telecom FR
            '5432':  {'distance_km': 25, 'include_countries': ['Belgium'], 'mainland_only': False},                      # Proximus BE
            '5466':  {'distance_km': 25, 'include_countries': ['Ireland'], 'mainland_only': False},                      # eir (IE)
            '55836': {'distance_km': 25, 'include_countries': ['India'], 'mainland_only': False},                        # Reliance Jio (IN)
            '5607':  {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': False},                          # Telekom Romania
            '5610':  {'distance_km': 25, 'include_countries': ['Czechia'], 'mainland_only': False},                      # O2 Czech Republic
            '5617':  {'distance_km': 25, 'include_countries': ['Poland'], 'mainland_only': False},                       # Orange Polska
            '5650':  {'distance_km': 25, 'include_countries': ['US'], 'mainland_only': False},                           # Frontier
            '5769':  {'distance_km': 25, 'include_countries': ['Canada'], 'mainland_only': False},                       # Videotron (CA)
            '577':   {'distance_km': 25, 'include_countries': ['Canada'], 'mainland_only': False},                       # Bell Canada
            '6327':  {'distance_km': 25, 'include_countries': ['Canada'], 'mainland_only': False},                       # Shaw Communications (CA)
            '6799':  {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': True},                           # Vodafone Greece
            '6805':  {'distance_km': 25, 'include_countries': ['Germany'], 'mainland_only': False},                      # Telefónica Germany (DE)
            '6830':  {'distance_km': 25, 'include_continents': ['EU'], 'mainland_only': False},                          # Liberty Global (EU footprint)
            '701':   {'distance_km': 25, 'include_countries': ['US'], 'mainland_only': False},                           # Verizon (UUNET)
            '7018':  {'distance_km': 25, 'include_countries': ['US'], 'mainland_only': False},                           # AT&T
            '7922':  {'distance_km': 25, 'include_countries': ['US'], 'mainland_only': False},                           # Comcast
            '812':   {'distance_km': 25, 'include_countries': ['Canada'], 'mainland_only': False},                       # Rogers
            '8151':  {'distance_km': 25, 'include_countries': ['Mexico'], 'mainland_only': False},                       # Telmex / Uninet (MX)
            '8447':  {'distance_km': 25, 'include_countries': ['Austria'], 'mainland_only': False},                      # A1 Telekom Austria
            '8473':  {'distance_km': 25, 'include_countries': ['Sweden'], 'mainland_only': False},                       # Bahnhof
            '852':   {'distance_km': 25, 'include_countries': ['Canada'], 'mainland_only': False},                       # TELUS
            '8708':  {'distance_km': 25, 'include_countries': ['Romania'], 'mainland_only': False},                      # RCS & RDS / Digi (RO)
            '8881':  {'distance_km': 25, 'include_countries': ['Germany'], 'mainland_only': False},                      # Versatel (DE)
            '8953':  {'distance_km': 25, 'include_countries': ['Romania'], 'mainland_only': False},                      # Telekom Romania
            '9143':  {'distance_km': 25, 'include_countries': ['Netherlands'], 'mainland_only': False},                  # Ziggo NL
            '9498':  {'distance_km': 25, 'include_countries': ['India'], 'mainland_only': False},                        # Airtel (IN)
            '9808':  {'distance_km': 25, 'include_countries': ['China'], 'mainland_only': False},                        # China Mobile Guangdong (CN)
            '9829':  {'distance_km': 25, 'include_countries': ['India'], 'mainland_only': False},                        # BSNL (IN)
        }

        with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
            for topo_name in topo_names:
                background = []
                if topo_names[topo_name]:
                    background = topohub.geo.generate_map(**topo_names[topo_name])
                executor.submit(gen.save_topo, topo_name, filename=f'data/caida/{topo_name}', with_plot=True, with_utilization=True, with_path_stats=True, with_topo_stats=True, background=background, scale=True, **topo_names[topo_name])


if __name__ == '__main__':
    main(sys.argv[1:])
