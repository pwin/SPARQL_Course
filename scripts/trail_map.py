# -*- coding: utf-8 -*-
"""An SVG of the trail, plotted from the real coordinates.

No coastline: drawing a bad outline of Great Britain would be worse than
drawing none, and the shape that matters here is the network, not the island.
Longitude is stretched by cos(mean latitude) so the plot is not distorted
east-west -- the same correction module 09 teaches.
"""
from __future__ import annotations

import math

import content as C
import content_works as W

W_PX, H_PX = 620, 720
PAD = 34


def build(shop_xy: dict[str, tuple[float, float]]) -> str:
    lons = [xy[0] for xy in shop_xy.values()]
    lats = [xy[1] for xy in shop_xy.values()]
    mean_lat = sum(lats) / len(lats)
    k = math.cos(math.radians(mean_lat))          # squash longitude to match

    x0, x1 = min(lons) * k, max(lons) * k
    y0, y1 = min(lats), max(lats)
    sx = (W_PX - 2 * PAD) / (x1 - x0)
    sy = (H_PX - 2 * PAD) / (y1 - y0)
    s = min(sx, sy)
    ox = PAD + ((W_PX - 2 * PAD) - (x1 - x0) * s) / 2
    oy = PAD + ((H_PX - 2 * PAD) - (y1 - y0) * s) / 2

    def px(lon, lat):
        return (ox + (lon * k - x0) * s, H_PX - oy - (lat - y0) * s)

    shops = {s_[0]: s_ for s_ in C.SHOPS}
    towns = {t[0]: t for t in C.SETTLEMENTS}

    # the two components, so the disconnected pair can be coloured differently
    adj: dict[str, set] = {}
    for a, b, _ in W.TRAIL:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    seen, stack = set(), ["inkwell"]
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        stack.extend(adj.get(n, ()))

    out = [f'<svg viewBox="0 0 {W_PX} {H_PX}" class="map" role="img" '
           'aria-labelledby="map-t map-d">',
           '<title id="map-t">The Bookshop Trail</title>',
           '<desc id="map-d">Thirty-three bookshops plotted at their real '
           'coordinates, joined by the walking trail. Two shops in the south '
           'west form a second, unconnected component.</desc>']

    for a, b, waymarked in W.TRAIL:
        x1_, y1_ = px(*shop_xy[a])
        x2_, y2_ = px(*shop_xy[b])
        cls = "seg" + ("" if waymarked else " unmarked")
        if a not in seen:
            cls += " orphan"
        out.append(f'<line class="{cls}" x1="{x1_:.1f}" y1="{y1_:.1f}" '
                   f'x2="{x2_:.1f}" y2="{y2_:.1f}"/>')

    labelled = {"inkwell", "colophon", "northern-light", "sea-margin",
                "endpapers", "cotton-quarto", "ex-libris", "castle-steps",
                "penwith", "west-quay", "dales-folio"}
    for sid, (lon, lat) in shop_xy.items():
        x, y = px(lon, lat)
        town = towns[shops[sid][2]][1]
        booktown = towns[shops[sid][2]][6]
        cls = "shop"
        if booktown:
            cls += " booktown"
        if sid not in seen:
            cls += " orphan"
        out.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" '
                   f'r="{5.0 if booktown else 3.4}"><title>{shops[sid][1]}, '
                   f'{town}</title></circle>')
        if sid in labelled:
            anchor = "end" if lon > -2.2 else "start"
            dx = -9 if anchor == "end" else 9
            out.append(f'<text class="pin" x="{x + dx:.1f}" y="{y + 3.6:.1f}" '
                       f'text-anchor="{anchor}">{town}</text>')

    out.append(f'<text class="mapnote" x="{PAD}" y="{H_PX - 10}">'
               'Larger dots are the three real book towns. The pale pair, '
               'bottom left, connects to nothing.</text>')
    out.append("</svg>")
    return "\n".join(out)
