pages

http://localhost:8000  (and /index.html)
    - THE FRONT END — the clean day-of viewer

http://localhost:8000/schedule_editor.html
    - day before editor. should produce baked files 
    - event specific

http://localhost:8000/data_editor.html
    - week before editor. should produce baked files 
    - park specific

tester → NOT a page. A MODE on the read viewer, reached by url params:
    http://localhost:8000/index.html?tester=1
    (editor_is_the_viewer: V2 is V1 with more controls, not a fork. The test
     fixtures already ride URL params — ?clock= for the date offset.)
    - week before tester
    - has limited sidebar
    [x] date shifting feature clock=YYYY-MM-DDTHH:MM fixture (viewer_core.js).
    [x] lat long shifting feature → ?tester=1
    
    [ ] on-tester EDIT FAB (Locate + Edit side by side) — waits on the editor porting into the
        extracted read core (still in panel.js / old_index.html). The .tester class + the
        right:80px FAB slot are already reserved.
    full test link: /index.html?tester=1&clock=YYYY-MM-DDTHH:MM

Working:
http://localhost:8000/mapborder_compare.html



http://localhost:8000/old_index.html
    - legacy all in one page (parked, not deleted)


