# Soka Everywhere

TL;DR:
- The thing that flipped this from "cute note app" to "maybe an OS" is small and specific: a belt operates on a *group* by a *rule*. Alt-tab cycles one thing at a time and forgets everything. That's not a faster switcher, it's a different category, and it's the first answer to alt-tab muscle memory that doesn't just lose to it.
- soka isn't an app, it's an interaction language -- the components/systems/verbs already running inside it. Extract it from LiveView-and-notes and re-host it on two substrates: a TUI (the lab, the oracle) and a Linux-native orchestrator (the product). Same grammar, swap the renderer.
- The Wayland bridge is real and has three rungs, cheapest first. The "my OS is soka and I jump through a creator's homepage" dream is coherent because everything is a tile -- and the part that eats years isn't the grammar, it's trust. Honest about which is which below.

#prose #soka #vision #wayland #tui #everything-is-a-tile #portal

-----

I'll say the quiet part first, because it's the part I half-believed and you should get to decide if I'm blowing smoke: for years the answer to "spatial desktops are better" was a shrug, because alt-tab always won. Alt-tab is muscle memory and muscle memory beats theory. Every tiling-WM evangelist runs into the same wall -- their layout is prettier and their hands still mash alt-tab.

Then you said *belts*, and something moved.

Here's why it's not nothing. Alt-tab is a recency stack: invisible until you summon it, one window at a time, no memory of where anything is. It degrades the moment you have more than three things open. A belt is the opposite shape. You grab a fistful of artifacts, drop them on a belt, the belt carries them to a sorter, and the sorter routes them *by a rule you set.* That's operating on a group. By a rule. Without naming each one. There is no gesture in alt-tab's whole vocabulary for that, because alt-tab can't hold a group and can't carry a rule. So this isn't "alt-tab but faster." It's a move alt-tab structurally cannot make. That's the first time the spatial pitch has had a weapon instead of an argument.

And the weapon is already built. The brain's `northstar/30_architecture/03_zettel_world.md` already names the belt (`conveyor`) and the sorter (`router` -- "multi-output choice tile for content- or rule-based branching"). You didn't invent a feature. You found the thing your own roadmap was already pointed at, and aimed it at windows instead of notes.

## soka is a grammar wearing an app

The reframe that makes "everywhere" possible: soka isn't a note-taking program that happens to be spatial. It's an interaction *language* that happens to currently render notes in a browser. The `terms_dictionary` already wrote the architecture without meaning to -- "components declare what a tile is, systems own what it does, and panels/surfaces decide how it is shown." The first two are the language. The third is the substrate. They've just always been fused inside one host, so nobody pulled them apart.

Pull them apart and you can re-host the grammar anywhere. Two places to start:

A **TUI** -- soka's tile grid drawn as cells of text in a terminal. This is the lab. Not a toy, a lab. A window in a TUI is a cheap deterministic rectangle of characters, so it's where you pin down what the language actually *means*: what does `route` do when the belt's target is occupied, what does `eject` do at a world edge, what happens when a buffer overflows. `03_zettel_world.md` already says the Conway experiments are "runtime proofs" -- the TUI is that, promoted to a deliverable. And it keeps the expensive substrate honest: when the real desktop does something weird, you reproduce it in the TUI, and triangulation tells you which leg lied. TUI and orchestrator are two views of one grammar. When they disagree, one of them is wrong, and now you can tell which.

A **Linux-native orchestrator** -- the same grammar, but the tiles are your actual windows, icons, and workspaces. This is the product. This is "soka everywhere."

The seam between them is the renderer, and here's the nice part: the brain spent a long time refusing to build a renderer abstraction, on purpose. `06_deepening.md`'s two-adapters rule -- don't build a swappable interface for one implementation. soka was right to wait. A TUI renderer *and* a Wayland renderer is the first time the render axis honestly has two adapters. The discipline didn't block the dream. It was waiting for it.

## Everything is a tile, escalated to the whole screen

`02_turtles.md`: a wall is a tile with `:blocking`, a portal is a tile with `:portal`, a clock is a tile with `:clock`. Your leap is one word longer: a browser is a tile with `:window`, an icon is a tile with `:icon`. And `:icon` is *already a shipped component.* "Icons are a tile" isn't a proposal in the orchestrator -- it's true in soka today. That's the proof the generalization holds: the vocabulary re-points at the OS with almost nothing new.

Watch the existing primitives land on real windows, no new nouns:

The pocket queue -- the held stack of zettels -- becomes your stack of held windows. Pick one up, carry it across monitors, set it down. `:portal` becomes teleport-this-window-to-that-workspace. `:blocking` becomes pin-this-in-place. The belt and the sorter are the belt and the sorter. Grab three browser tabs (tabs are tiles too), drop them on the belt, the router sorts `research` into one workspace and `shopping` into another while you go get coffee. The exact same machinery, in the TUI, sorts test fixtures into test buffers -- which is how you trust it before it touches anything real.

The deeper claim under all of it: today, alt-tab, the file manager, the app launcher, and the tab bar are four separate ad-hoc spatial languages, each with its own muscle memory, none of them talking. soka collapses them into one grammar. You don't learn window management apart from file management apart from tab management. It's all `pick_up`, `place`, `route`, over tiles. One language for everything on the glass.

(One caution so "area" doesn't grow fangs: when you say "each area is a thing," map it onto what's already here -- a `layer`, or a container-tile, or a kasten. The brain has containers. Don't let "area" become a fourth undefined spatial noun. Ubiquitous language or bust.)

## The Wayland bridge, for real

This is the question you actually asked, so here's the honest mechanism, not a wave.

Wayland is a *protocol*, not a program. The thing that surprises people coming from X11: in Wayland the compositor is the display server and the window manager and the thing that draws to the screen -- all one process. Sway is a compositor. Hyprland is a compositor. GNOME's Mutter is a compositor. There's no separate "window manager" to slot in beside it.

Apps are *clients.* A client (Firefox, your terminal) draws its own pixels into a buffer and hands the buffer to the compositor over a socket. The compositor doesn't paint Firefox -- Firefox paints Firefox. The compositor decides *where that buffer goes,* stacks it with the others, and routes your keyboard and mouse to whichever surface has focus. A normal app window shows up in the protocol as an `xdg_toplevel`. Hold that word -- that object is your window-tile.

The hard plumbing (talking to the GPU and the screen via DRM/KMS, reading input devices via libinput, speaking the protocol) is done for you by a library: **wlroots** (C, what Sway and Hyprland use) or **Smithay** (Rust). You don't write that from scratch.

So the bridge is three rungs, and you do not have to start at the top:

1. **TUI.** soka renders its own grammar in a terminal. No OS windows involved at all. Proves the language is real and gives you the oracle. Cheapest thing that could possibly work.

2. **soka drives Sway over its IPC.** Sway already exposes a socket (`swaymsg` is the toy version of it). soka stays an ordinary program -- doesn't own the screen, doesn't touch the GPU -- and just *tells Sway where to put the real windows.* Real desktop, real apps, and you wrote zero compositor code. This is the rung people skip and shouldn't. It's where "soka moves my actual windows" becomes true for the first time, on a weekend instead of a year.

3. **soka is the compositor.** A wlroots or Smithay compositor that owns surfaces and input directly. Now the dream is unmediated -- there's no Sway in the middle, soka *is* the desktop.

On rungs 2 and 3 the architecture stays the one from the brain's gut instinct -- keep the durable model small, in one place. The grammar lives in Elixir. An app window arrives as an `xdg_toplevel`, soka represents it as a tile with a `:window` component holding the surface handle, and soka answers one question: where does this tile live, how big, which workspace. The compositor maps tile-geometry back to the surface and composites. **soka never draws the app. It moves the container.** That boundary is the honest one and it's also the freeing one -- you are never on the hook for rendering Firefox.

The one place rung 3 will bite, and I won't pretend otherwise: latency. You cannot round-trip every mouse delta to a BEAM process and back at 144Hz and still feel good. So the real seam is continuous-vs-discrete. The compositor handles the high-frequency stuff locally -- cursor, the live drag preview, animation. soka handles the discrete grammar verbs -- route, place, eject, which workspace, run the sorter. The belt's *decision* is soka's; the belt's *animation* is the compositor's. Get that line right and it sings. Get it wrong and it feels like typing through molasses. (Also: plenty of apps still aren't native Wayland and come in through XWayland. Extra surface types, extra quirks. Real, not fatal.)

## The dream, and where the dragons actually are

You said it plainly: your OS is soka, you launch the soka homepage of a creator you follow, and you jump *through* it, seamlessly.

The thing that makes this coherent instead of fan-fiction is the everything-is-a-tile move. A creator's "homepage" is a soka world -- a layer of tiles. "Jumping through" is a portal, and `:portal` is already a component that warps you between layers. So far this is just soka doing what soka does, except the far side of the portal is *someone else's* world. And whether the far side is a note-world, a website, or a native app, it arrives the same way -- as tiles in your world -- because that's the only thing soka knows how to receive. That sameness is the entire reason "seamless" is even a sentence you can say. The grammar doesn't care whose world it is or what's on the other side. It's all tiles.

So the dream doesn't break on the grammar. It breaks somewhere else, and it's worth being clear-eyed about where, because that's where the years go:

It's seamless *across a trust boundary.* A stranger's world becoming part of your machine is not a layout problem, it's a security problem. What runs? What can a remote tile touch? What's it allowed to do with your pocket, your files, your input? That's the dragon. Not "can we draw it" -- we can. "Can we let it in without handing a stranger the keys." Federated everything has always foundered there, and soka won't be magically exempt.

So here's the honest ledger, since you asked me not to blow smoke:

**Load-bearing and real:** the belt/sorter changing the alt-tab math -- that's a genuine category difference, not a vibe. The grammar extraction -- components/systems already are the language, this is lifting not inventing. Rungs 1 and 2 of the bridge -- a TUI and a soka-drives-Sway proof are buildable now, by you, this year. Everything-is-a-tile generalizing to windows -- `:icon` already proves it.

**Smoke, or at least fog:** rung 3 at 144Hz with a remote brain is a real latency design problem, not a given. The federated "jump into a stranger's world" seamlessness is a trust problem that's defeated better-funded people than us. And the whole thing is *enormous* -- the brain's own "keep the durable model small" instinct is the only thing that keeps it from ballooning into vapor.

The move that respects both columns: build the cheap rung first. The TUI costs you a renderer and buys you the proof that the language is real and the oracle that keeps the rest honest. If the grammar feels good moving fake windows in a terminal, the dream has a spine. If it doesn't, you found out for the price of a weekend instead of a compositor.

But you know how dreams are. The point of writing this one down isn't to schedule it. It's so that the next time someone says "spatial desktops never beat alt-tab," there's a doc that says: the belt does. Start there.

## The graveyard, and why we're not in it

"Hasn't this been tried?" deserves a real answer instead of a flinch, because it has, for forty years, and most of it is dead. The graveyard is crowded. What's useful is that the headstones don't all say the same thing -- each family died of something specific, and every one of those deaths is a lesson pointed straight at us.

The 3D desks went first. BumpTop -- Anand Agarawala's Toronto thesis, the viral TED demo, shipped 2009 -- turned your files into physics-simulated piles you shoved around a virtual desk. Project Looking Glass was Sun doing the same in Java3D. BumpTop got *good* early press and still flopped; people called the 3D gimmicky, Google bought the team in 2010 and switched it off. Looking Glass just went quiet. They died of the same thing: physical realism is friction dressed as power. A wobbling stack looks magic in a demo and costs you a motion every single time after. That's the first trap and it's ours too -- the moment the world-aesthetic makes the common action cost more than it saves, we've rebuilt BumpTop.

The research lineage was the one that was actually *right*, and it still didn't take. Rooms (Xerox PARC, Henderson and Card, 1986) is the literal grandfather of virtual desktops. Data Mountain (Microsoft Research, late 90s) and Task Gallery put documents on a tilted plane and in a 3D gallery, and the studies confirmed what we're betting on -- humans remember "it's top-left" far better than they remember a recency list. The win was real. It was also marginal, and the good part got quietly absorbed: Rooms became the workspaces every OS now ships, minus the spatial-memory thesis. The lesson is the uncomfortable one. "Spatial memory beats recency" is true and it is *not enough by itself* to move anyone. It needs a second reason to exist. (The belt is the second reason. Hold that thought.)

The zooming interfaces are our closest blood relatives and they teach the scariest lesson. Pad, Pad++, Jazz (Perlin, Bederson, Hollan, early 90s), Raskin's ZUI work, Eagle Mode still alive today -- everything lives on one infinite zoomable plane, no windows, you pan and zoom instead of switching. That is *soka's infinite world grid* with the serial numbers filed off. They died of disorientation: where am I on the endless plane, and how do I get home. An infinite world with no anchor is a place to get lost. The avatar and the fixed landmarks are the answer the ZUIs never had -- which means they're not decoration, they're the thing keeping us out of that grave.

The spatial file managers lost a fight we will also have to fight. The original Mac Finder was near-religious about it -- one file, one place, every folder a window that remembers where it sits -- and GNOME's Nautilus shipped a spatial mode in 2004 and ripped it out by 2008 amid open revolt. They lost to browser-style navigation: back, forward, one reused window. Spatial purity meant window explosion and, plainly, *more work*. Convenience won, decisively. Spatial-correctness is not a virtue people will pay keystrokes for. The flow has to be less work than the boring way on day one, not merely more principled.

The eye-candy compositors tell you exactly where the market set the bar. Compiz and Beryl gave us the spinning cube and wobbling windows, and all of it faded to ornament because the 3D was presentation, not interaction -- you could admire your windows, not do anything to them. Watch what *survived* instead: Exposé and Mission Control. A spatial spread whose entire job is to help you pick one window and then vanish. A prettier alt-tab. That's the deal the desktop world actually offered spatial UI -- you may exist, as long as you reduce to "pick one thing faster." Everything that tried to be more got turned off.

The tiling window managers are the one corner that genuinely won, and the live frontier is the part worth watching. i3, sway, xmonad, bspwm proved a real audience will trade configuration for deterministic, keyboard-driven placement -- actual spatial memory, no mouse fumbling. And the recent wave is spiritually right next door to us: PaperWM (a GNOME extension) and niri (a Rust Wayland compositor, started 2023, shipping steadily, plenty of people daily-driving it) throw out the fixed grid for an *infinite horizontal strip of columns* -- open a window and nothing else resizes, you just scroll the strip. That paper-roll is the closest anyone has come to soka's infinite world. But it stops exactly where we start: PaperWM and niri are about where the window *sits*. They are the best answer ever built to "where does it go," and they have no answer at all to "grab this group and route it by a rule." They arrange. They don't operate.

And the newest money, spatial computing -- visionOS on the Vision Pro, HoloLens before it -- floats your windows around a room. Real spatial memory, bought by making the input *worse*: a headset and hand-tracking instead of a desk. Still placement in 3D. Still no machines.

Lay all seven out and the same thing is screaming from every headstone: **they are all about where windows sit and how you recall them. Not one is about what you can do to a group of them, by a rule.** They optimized placement and memory. The survivors are precisely the ones that gave up and became a nicer way to pick one window. Nobody shipped machines -- belts that carry a group, routers that sort by rule, buffers that hold. That axis, *programmable* spatial instead of merely *arranged* spatial, is basically untouched on the desktop. Which is the actual reason the belt isn't BumpTop with extra steps: BumpTop made the desk prettier; the belt makes the desk work on your behalf. Different axis. Empty graveyard plot.

Here's the reframe that's the strongest version of the whole thing. soka's lineage was never the spatial-desktop tradition -- it's the factory-game tradition. The inspiration folder is Sokoban and Chip's Challenge; the belt-and-sorter is Factorio. That matters enormously, because "belts and routers operating on a group by rule" is a *solved, beloved, deeply learnable* interaction -- in games. Millions of people already have that muscle memory and reach for it for fun. We're not re-attempting the desktop idea that keeps dying. We're importing a proven grammar from the one domain where it's a triumph. That's a far better place to start than any plot above.

So the three things to keep nailed to the wall, because they're the deaths history actually hands out:
- the BumpTop trap -- don't let the aesthetic add friction to the common action.
- the ZUI trap -- the infinite world needs an unmistakable home, or people get lost in it.
- the spatial-Finder trap -- the flow has to save keystrokes on day one, not just be righteous.

Sources, for when someone wants to go dig: niri ([github.com/niri-wm/niri](https://github.com/niri-wm/niri), [LWN tour](https://lwn.net/Articles/1025866/)); BumpTop ([Wikipedia](https://en.wikipedia.org/wiki/Bumptop), [How-To Geek on the 3D-desktop die-off](https://www.howtogeek.com/843659/what-happened-to-3d-desktops-like-bumptop/)); Project Looking Glass ([Wikipedia](https://en.wikipedia.org/wiki/Project_Looking_Glass)); Data Mountain ([Microsoft Research](https://www.microsoft.com/en-us/research/publication/data-mountain-using-spatial-memory-for-document-management/)).
