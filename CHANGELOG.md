# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## 1.0.0 (2022-01-28)


### Features

* add __init__.py with addon information ([77a92de](https://github.com/hugemenace/blender-nd-addon/commit/77a92deb218f1078e86046e0529ba0bc0bc342b4))
* add active and alt_mode key indicators to operator overlays ([bde234c](https://github.com/hugemenace/blender-nd-addon/commit/bde234ce47d319207c622325903712878bcab8f4))
* add custom HUD UI for all operators and allow viewport navigation event passthrough ([e032770](https://github.com/hugemenace/blender-nd-addon/commit/e032770664530ae59f8c749b8bf9664af2116c22))
* add initial menu ([a6329b3](https://github.com/hugemenace/blender-nd-addon/commit/a6329b3cb55c37f4c8a17c69555df8359b4d7bfc))
* add initial UI panel ([789f471](https://github.com/hugemenace/blender-nd-addon/commit/789f4715ee39aad893d2c0eddf36798eaa3b2867))
* add new_sketch operator ([3aca34b](https://github.com/hugemenace/blender-nd-addon/commit/3aca34bb96ceb836eb704a83223df85d02fa48f7))
* add overlay pinning option for all operators ([8bff7c4](https://github.com/hugemenace/blender-nd-addon/commit/8bff7c480cbca251e8e87191d5e2baaf4d886384))
* add spinner operator ([26c1aea](https://github.com/hugemenace/blender-nd-addon/commit/26c1aea60e47ae24b379a23989cf1eb301d72cb8))
* add spinner to UI panel and menu, reorganise operators, update icons ([bbc1002](https://github.com/hugemenace/blender-nd-addon/commit/bbc1002b11930d366c7befb6004068759432d7aa))
* add thickener modifier ([f215357](https://github.com/hugemenace/blender-nd-addon/commit/f215357a674f0c1abc5ec586d3202fcd7d23e014))
* add view alignment operator, and relatedly fix incorrect overlay redraw implementation — subsequently applied across all other operators ([7eabac6](https://github.com/hugemenace/blender-nd-addon/commit/7eabac6c3752afb8f2aad846094d8cc0e661498a))
* allow duplicate selection shortcut pass-through in new_sketch operator ([86255a0](https://github.com/hugemenace/blender-nd-addon/commit/86255a00717b49813c6fb5c9a0bf487706b36cbd))
* allow mm based factors to be scaled up and down on all operators ([c433400](https://github.com/hugemenace/blender-nd-addon/commit/c433400a215c51d49eb3b56a2b9d810a38187e38))
* create a dedicated overlay manager, drawing utilities, and update all operators respectively ([1520b36](https://github.com/hugemenace/blender-nd-addon/commit/1520b36caa328c69cbb98cea7271bb8a259ac0d1))
* ensure cutter bolts are clearly visible in the viewport, including their depth into the target ([d6d08f2](https://github.com/hugemenace/blender-nd-addon/commit/d6d08f2268c0997494dd13bcffa5d0b0a8997814))
* step bolt operator segments up by 2, and by 1 on shift, following similar operation to the sketch_bevel operator ([8dbece2](https://github.com/hugemenace/blender-nd-addon/commit/8dbece2e606f3ffe55072f4e8a3a07badf400584))
* unify input controls across all operators and add revert/cancel functionality ([5a79040](https://github.com/hugemenace/blender-nd-addon/commit/5a7904086860e2e5a27c3f378ec3ee350e3576ff))


### Bug Fixes

* add poll method to operators to ensure all conditions are correct before they can be invoked ([4faad28](https://github.com/hugemenace/blender-nd-addon/commit/4faad280d8c45fc382c7dcc4d89439a6c43ddbd7))
* add shade_smooth call to faux_bevel operator and remove legacy mouse_x/y variables ([0d994b7](https://github.com/hugemenace/blender-nd-addon/commit/0d994b70a4be68afef30ad21677551ea5def2cfe))
* add smooth shading step to faux bevel operator ([5f09d2c](https://github.com/hugemenace/blender-nd-addon/commit/5f09d2ca31f5bc6451bb016531b12a0734bead4f))
* ensure faux bevel weighted normal weight is set to 100% to avoid face-level artifacts ([0849dfd](https://github.com/hugemenace/blender-nd-addon/commit/0849dfd2a02cb53eb8595fd1a81fa2b5021c995d))
* ensure new sketches can only be created in object mode with no objects selected ([d77f839](https://github.com/hugemenace/blender-nd-addon/commit/d77f839470f4c1e7fcebba31ccf9f8f5e81ed9ea))
* ensure utils.set_3d_cursor handles the different possible cursor rotation modes ([b7100ec](https://github.com/hugemenace/blender-nd-addon/commit/b7100ec0fc6cc9758ecfeedc77736331ef64cac6))
* fix operator labels ([18023dc](https://github.com/hugemenace/blender-nd-addon/commit/18023dc885ebafd2842f0d611ab81389624757e7))
* fix register/unregister call for menu in __init__.py ([7683f8d](https://github.com/hugemenace/blender-nd-addon/commit/7683f8d35e1b7e3984e1f66fa1409e3722e77918))
* fix up file names and register all scripts from __init__.py ([94dd2b9](https://github.com/hugemenace/blender-nd-addon/commit/94dd2b9899444a7cc6a426949a2dbdfcab7cde30))
* set alt mode to constant False on segment property overlay of bolt operator ([99e4a12](https://github.com/hugemenace/blender-nd-addon/commit/99e4a1216a928e7b4dc22b3a57e503b27821f31b))
* set merge_threshold to 0.1mm for screw modifiers on bolt operator ([5d0c064](https://github.com/hugemenace/blender-nd-addon/commit/5d0c064041648e4127065e6b4b7afe1ad3135d62))
* standardize operator names ([c25991e](https://github.com/hugemenace/blender-nd-addon/commit/c25991e148df21cbff4bb209c7dda2bc1fca2135))
* update all operator, panel, and menu class names to follow Blender's naming convention and add execute method to operators for menu support ([86c96dd](https://github.com/hugemenace/blender-nd-addon/commit/86c96ddfe171b5aaa61a6c4ba17189fcc6081925))
