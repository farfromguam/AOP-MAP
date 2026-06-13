pages

http://localhost:8000  (and /index.html)
    - THE FRONT END — the clean day-of viewer (was viewer.html, promoted at the slice-7 swap).

http://localhost:8000/old_index.html
    - legacy all in one page (parked, not deleted).

http://localhost:8000/viewer.html
    - day of viewer  → now lives at / (index.html). This URL no longer exists.
    [x] move the locate button to bottom right make it a blue crosshair. make it look like like the edit button. place it next to where the edit button lives. we wont show the edit button here, but on the tester view, both will show up.
        -- done: bottom-right blue crosshair FAB, styled like the edit FAB (.panel.collapsed). Locate is always present so it anchors the far-right corner (right:12px); edit FAB hidden on this read view and, on tester, sits to locate's LEFT (right:80px). (brain/tasks/13_viewer_extraction/viewer_swap.md)

http://localhost:8000/schedule_editor.html
    - day before editor. should produce baked files 
    - event specific

http://localhost:8000/data_editor.html
    - week before editor. should produce baked files 
    - park specific

tester  →  NOT a page. A MODE on the read viewer, reached by a link:
    http://localhost:8000/index.html?tester=1
    (editor_is_the_viewer: V2 is V1 with more controls, not a fork. The test
     fixtures already ride URL params — ?clock= for the date offset.)
    - week before tester
    - has limited sidebar
    [x] date shifting feature  → the existing ?clock=YYYY-MM-DDTHH:MM fixture (viewer_core.js).
    [x] lat long shifting feature → ?tester=1 wraps navigator.geolocation: the first real
        GPS fix pins to the park pavilion, later fixes keep their real delta, so walking the
        local neighborhood walks the blue dot around the PARK. Reuses the locate machinery
        untouched. (brain/tasks/13_viewer_extraction/viewer_locate_install_version.md addendum)
    [ ] on-tester EDIT FAB (Locate + Edit side by side) — waits on the editor porting into the
        extracted read core (still in panel.js / old_index.html). The .tester class + the
        right:80px FAB slot are already reserved.
    full test link: /index.html?tester=1&clock=YYYY-MM-DDTHH:MM


http://localhost:8000/mapborder_compare.html

