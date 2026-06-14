#!/usr/bin/env python3
"""Verify the TBI.copy rewrite landed in the live viewer (index.html on :8001).

About tab (plain DOM, GL-independent): intro, 5 reference items, the new
Driver's Meeting prose section (heading + 7 paragraphs + 5 rules), note.

Schedule (GL-independent): run the SAME canonical transform the calendar and the
map both consume -- window.AOPEventSchedule.eventScheduleToGeojson -- and assert
18 sessions, exactly ONE map anchor (#pavilion; keep pavilion / drop the rest),
the real session titles, and composed clock windows.

Calendar DOM + screenshots are best-effort: headless WebGL is flaky here (the
documented "could not compile fragment shader" flake kills the map pipeline that
feeds the calendar). Tried under software GL; reported, not fatal. The transform
check is authoritative because the calendar <li> rows are a thin map over it.
"""
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:8001/"

GL_FLAKE = ("fragment shader", "CONTEXT_LOST_WEBGL", "GL Driver Message",
            "GPU stall", "no style added to the map", "WebGL", "loseContext")
def is_flake(s): return any(k in s for k in GL_FLAKE)

real_errors = []
flake_msgs = []

def main():
    with sync_playwright() as p:
        b = p.chromium.launch(args=[
            "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
            "--ignore-gpu-blocklist",
        ])
        pg = b.new_page()
        def on_console(m):
            if m.type in ("error", "warning"):
                (flake_msgs if is_flake(m.text) else real_errors).append(f"console.{m.type}: {m.text}")
        pg.on("console", on_console)
        pg.on("pageerror", lambda e: (flake_msgs if is_flake(str(e)) else real_errors).append(f"pageerror: {e}"))
        pg.goto(URL, wait_until="networkidle")
        pg.wait_for_function("window.AOPViewer && window.AOPViewer.map", timeout=15000)
        pg.wait_for_function("typeof window.AOPEventSchedule === 'object'", timeout=10000)
        pg.wait_for_timeout(2500)

        about = pg.evaluate("""() => {
          const root = document.getElementById('aboutInfoPanel');
          const txt = root.textContent || '';
          return {
            h2: root.querySelector('h2')?.textContent || '',
            intro: root.querySelector('p.info-copy')?.textContent || '',
            items: [...root.querySelectorAll('ul.info-list > li .info-label')].map(e => e.textContent),
            subhead: root.querySelector('h3.info-subhead')?.textContent || '',
            copyCount: root.querySelectorAll('p.info-copy').length,
            rulesCount: root.querySelectorAll('ul.info-rules > li').length,
            note: root.querySelector('p.info-note')?.textContent || '',
            hasWelcome: txt.includes('bright blue shirts'), hasCOW: txt.includes('C.O.W.'),
            hasRaffle: txt.includes('Appalachian RC for Kids'), hasWinch: txt.includes('Winching is free'),
            hasNoBashers: txt.includes('No bashers'), has22: txt.includes('2.2'),
            hasCall: txt.includes('caw-craaawl'),
            noTrailBuddies: !/trail budd/i.test(txt),
          };
        }""")

        # GL-independent: the one transform the calendar + map both read.
        xf = pg.evaluate("""async () => {
          const cfg = await (await fetch('./data/aop_event_schedule.json')).json();
          const built = window.AOPEventSchedule.eventScheduleToGeojson(cfg);
          const feats = built.geojson.features;
          const anchors = feats.filter(f => f.properties.feature_kind === 'event_anchor');
          const sessions = feats.filter(f => f.properties.feature_kind === 'event_session');
          return {
            title: built.geojson.metadata.event.label,
            status: built.geojson.metadata.status,
            anchorTags: anchors.map(f => f.properties.location_tag),
            sessionCount: sessions.length,
            names: sessions.map(f => f.properties.title),
            days: [...new Set(sessions.map(f => f.properties.day))],
            sampleWindow: sessions.find(f => f.properties.session_id === 'sat-driver-meeting')?.properties.window,
            sessionsWithGeom: sessions.filter(f => f.geometry).length,
          };
        }""")

        # Screenshots + live calendar DOM. The calendar lazy-renders on tab
        # activation, so read #calendarDays AFTER clicking into Events (else it
        # reads the pre-render empty state and lies).
        shot = False
        try:
            pg.click("#leftTabAbout"); pg.wait_for_timeout(400)
            pg.screenshot(path="brain/output/tbi_about.png")
            pg.click("#leftTabEvents"); pg.wait_for_timeout(700)
            pg.screenshot(path="brain/output/tbi_events.png")
            shot = True
        except Exception as e:
            real_errors.append(f"screenshot: {e}")
        cal = pg.evaluate("""() => {
          const rows = [...document.querySelectorAll('#calendarDays > li:not(.calendar-empty)')];
          return { count: rows.length,
                   first: rows[0] ? (rows[0].querySelector('.calendar-name')?.textContent || '') : '' };
        }""")
        b.close()

    checks = []
    def chk(n, c, got=""): checks.append((n, bool(c), got))

    chk("about h2", about["h2"] == "About the Rock Warblers", about["h2"])
    chk("about intro welcomes", about["intro"].startswith("Welcome to the first event"), about["intro"][:36])
    chk("5 reference items", about["items"] == ["Mandatory skills","Rigs","The park","The map","The crew"], about["items"])
    chk("driver-meeting subhead", about["subhead"] == "Driver's Meeting", about["subhead"])
    chk("9 info-copy paras", about["copyCount"] == 9, about["copyCount"])
    chk("5 rules", about["rulesCount"] == 5, about["rulesCount"])
    chk("note present", "See you at the pavilion" in about["note"], about["note"])
    chk("welcome text", about["hasWelcome"]); chk("C.O.W. text", about["hasCOW"])
    chk("raffle/charity text", about["hasRaffle"]); chk("winching-free rule", about["hasWinch"])
    chk("rigs: no bashers", about["hasNoBashers"]); chk("rigs: 2.2 class", about["has22"])
    chk("trail buddies removed", about["noTrailBuddies"])
    chk("crew: Rock Warbler call (caw-craaawl)", about["hasCall"])

    chk("transform title", xf["title"] == "Rock Warblers Trail Blazing Invitational", xf["title"])
    chk("transform status live", xf["status"] == "live", xf["status"])
    chk("18 sessions", xf["sessionCount"] == 18, xf["sessionCount"])
    chk("ONE anchor = #pavilion", xf["anchorTags"] == ["#pavilion"], xf["anchorTags"])
    chk("days Fri/Sat/Sun", set(xf["days"]) == {"Friday","Saturday","Sunday"}, xf["days"])
    chk("driver-meeting window composed", xf["sampleWindow"] == "9:00 AM · Morning", xf["sampleWindow"])
    namejoin = " | ".join(xf["names"])
    for must in ["Arrive + camp setup","Rock Hard Adventure Tour","Show & Shine staging + judging",
                 "Warbler Peck and Pop Challenge","The Gravity Gauntlet","Hot dog dinner",
                 "PRO Line Before the Fire obstacle course race","Driver Doodles: Sketchy Driving Challenge",
                 "High Noon awards + 50/50 drawing"]:
        chk(f"session: {must}", must in namejoin)

    chk("no real (non-GL) errors", len(real_errors) == 0, real_errors)

    passed = sum(1 for _, ok, _ in checks if ok)
    print(f"\n==== TBI copy verify: {passed}/{len(checks)} checks ====")
    for n, ok, got in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {n}" + (f"  -> {got}" if not ok else ""))
    print(f"\nLive calendar DOM: {cal['count']} rows" + (f", first='{cal['first']}'" if cal['count'] else " (empty — headless GL flake; transform verified above)"))
    print(f"Screenshots written: {shot}  (brain/output/tbi_about.png, tbi_events.png)")
    if flake_msgs:
        print(f"\nIgnored headless-WebGL flake messages: {len(flake_msgs)}")
    sys.exit(0 if passed == len(checks) else 1)

main()
