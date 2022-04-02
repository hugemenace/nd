# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [1.15.0](https://github.com/hugemenace/nd/compare/v1.14.0...v1.15.0) (2022-04-02)


### Features

* add manifold option to blank_sketch operator ([aebd11b](https://github.com/hugemenace/nd/commit/aebd11b90723d69bcb981f9c8820fcbd8abae9c3))
* add profile_extrude operator ([331f2bb](https://github.com/hugemenace/nd/commit/331f2bbaaa3679387985d521f9be77cf26e47dfe))


### Bug Fixes

* ensure solidify modifier uses even offset ([57a5e59](https://github.com/hugemenace/nd/commit/57a5e591f3f0aeee8e64e12b841b92f5fa2998fa))

## [1.14.0](https://github.com/hugemenace/nd/compare/v1.13.0...v1.14.0) (2022-04-01)


### Features

* add mirror operator ([1196540](https://github.com/hugemenace/nd/commit/11965400980aed2298883fd7d575423fcecaeec3))
* automatically select and set active the boolean reference object ([8ea087c](https://github.com/hugemenace/nd/commit/8ea087c9c9c5419dbb55dc8d2cb39fa15335d3d9))


### Bug Fixes

* ensure that parented objects in all boolean operations have their transforms maintained ([82e58a2](https://github.com/hugemenace/nd/commit/82e58a23b8b1aa02f4a20bb26cdb6f624edceec8))

## [1.13.0](https://github.com/hugemenace/nd/compare/v1.12.0...v1.13.0) (2022-04-01)


### Features

* rename ring_and_bolt to recon_poly (regular convex polygon) as it more accurately represents its behaviour ([4837554](https://github.com/hugemenace/nd/commit/4837554c3d3e88f80bca86147d1d54938f0b66c8))

## [1.12.0](https://github.com/hugemenace/nd/compare/v1.11.2...v1.12.0) (2022-03-31)


### Features

* add boolean slice operator ([722dd8d](https://github.com/hugemenace/nd/commit/722dd8d651a4c98b11ecda8011e8e87f71cd2071))
* ensure reference and secondary objects in boolean operations are parented to the primary object ([7633792](https://github.com/hugemenace/nd/commit/7633792563919c0f088efcb76c5fa431b50c8d6c))
* prefix boolean reference object names ([6044792](https://github.com/hugemenace/nd/commit/60447921c2f98109e62f92a7474cdccd8298e821))

### [1.11.2](https://github.com/hugemenace/nd/compare/v1.11.1...v1.11.2) (2022-03-30)


### Bug Fixes

* ensure ESC key does not cancel paused operators ([01cfa93](https://github.com/hugemenace/nd/commit/01cfa9356c015f5aa7e6b4608c435cd5ca352d91))

### [1.11.1](https://github.com/hugemenace/nd/compare/v1.11.0...v1.11.1) (2022-03-30)

## [1.11.0](https://github.com/hugemenace/nd/compare/v1.10.0...v1.11.0) (2022-03-29)


### Features

* add the 3 core boolean operators, difference, union, and intersect ([ca58b0b](https://github.com/hugemenace/nd/commit/ca58b0b3d0db45d9444c0a75c465e28bf4858992))


### Bug Fixes

* swap origin and destination objects in set_origin operator ([8f84279](https://github.com/hugemenace/nd/commit/8f84279bda2cda7243209dbee61c4385cfc44699))

## [1.10.0](https://github.com/hugemenace/nd/compare/v1.9.0...v1.10.0) (2022-03-27)


### Features

* add version detection, "update available" notification, and Gumroad link to main UI panel ([c70b2ff](https://github.com/hugemenace/nd/commit/c70b2ff54bfc983ff4509e161b26ac1625add138))


### Bug Fixes

* fix erroneous unregister_draw_handler calls in screw, solidify, seams, and smooth operators ([02a52d8](https://github.com/hugemenace/nd/commit/02a52d8d4ea5dd706af2787acd25c0aa40db6ba3))

## [1.9.0](https://github.com/hugemenace/nd/compare/v1.8.0...v1.9.0) (2022-03-27)


### Features

* replace overlay fixed pin location with pin-in-place functionality ([2763a33](https://github.com/hugemenace/nd/commit/2763a33021e7dd9ed8ea8ccca0ca422553c7f5b5))


### Bug Fixes

* ensure seams operator turns on object auto smooth if override is set ([68b58ce](https://github.com/hugemenace/nd/commit/68b58ced069e0b51b6f5d324d812b82435e76600))
* fix screw operator summon & revert error ([f34b62d](https://github.com/hugemenace/nd/commit/f34b62d6f747e1ab1c611c1cc702a5d649e12a33))

## [1.8.0](https://github.com/hugemenace/nd/compare/v1.7.1...v1.8.0) (2022-03-26)


### Features

* add interactive UV seams & sharps operator ([a47891a](https://github.com/hugemenace/nd/commit/a47891ab6ce7afe351e74197102501b4f30ec1f8))

### [1.7.1](https://github.com/hugemenace/nd/compare/v1.7.0...v1.7.1) (2022-02-25)


### Bug Fixes

* ensure the decimate modifier retains its appropriate position in the stack when recalling the ring_and_bolt operator ([03117a2](https://github.com/hugemenace/nd/commit/03117a2ca804a5fee2935cfa9051c9b0674aac7c))

## [1.7.0](https://github.com/hugemenace/nd/compare/v1.6.1...v1.7.0) (2022-02-19)


### Features

* add smooth operator ([677309e](https://github.com/hugemenace/nd/commit/677309e8b5320c16596a72dc2fbe42b651f7879c))


### Bug Fixes

* ensure vertex_bevel operator always places current bevel modifier at the top of the stack, and only creates one weld modifier in total ([00cfd4e](https://github.com/hugemenace/nd/commit/00cfd4ebd47f09c87e6ab00f65d268c7c849371a))

### [1.6.1](https://github.com/hugemenace/nd/compare/v1.6.0...v1.6.1) (2022-02-18)


### Bug Fixes

* reduce remove double vertices threshold in blank_sketch operator ([511d311](https://github.com/hugemenace/nd/commit/511d3116988b72cc332596faef2646b2a86ada07))
* update scale parameter overlay representation in screw_head operator ([e153004](https://github.com/hugemenace/nd/commit/e1530046feab51c1fd4b070958f9a166ff65da91))

## [1.6.0](https://github.com/hugemenace/nd/compare/v1.5.0...v1.6.0) (2022-02-08)


### Features

* add 3 point view-plane creation via vertex select mode in view_align operator ([3406bd3](https://github.com/hugemenace/nd/commit/3406bd34e4c54ae35556caa8fb894cec66c1d914))
* add profile parameter to vertex bevel ([e9ecf35](https://github.com/hugemenace/nd/commit/e9ecf352c137202059c1f379a73ab301a3422b3f))
* add set_origin utility operator ([f271de7](https://github.com/hugemenace/nd/commit/f271de7a090ec38bf1df65b7d2a0ba8721491541))
* add summon behaviour to screw, solidify, and wn_bevel operators ([2464274](https://github.com/hugemenace/nd/commit/2464274a8e50486513189d79505c1bca8ababa92))
* add summon feature to ring_and_bolt operator ([b7f1ed7](https://github.com/hugemenace/nd/commit/b7f1ed77e3798371df8abc5f5accf20fe7ae7b6f))
* split face_sketch operator into geo_lift and view_align, with improvements in each respectively ([9b8d2d4](https://github.com/hugemenace/nd/commit/9b8d2d49569800f4909cad3c4add5b3c9e0402e8))


### Bug Fixes

* add vert, edge, face specific selection mode to geo_lift operator ([9e91e06](https://github.com/hugemenace/nd/commit/9e91e06083ac69571c57ba73f758ac1a23817889))
* ensure all target geometry is deselected when first entering geo_lift, or view_align operators ([83bc45d](https://github.com/hugemenace/nd/commit/83bc45d0a23d02619f79957d01b197b08a2ad27e))
* ensure cancel keybind cancels all operators, particularily while in halt mode ([126ec13](https://github.com/hugemenace/nd/commit/126ec13c4b4fac28fdcdb5849dba3a9bb6321676))
* ensure correct leftover geometry is removed based on selection mode in geo_lift operator ([0ea0be0](https://github.com/hugemenace/nd/commit/0ea0be0f9f397a6fe44fb47e21550e38727ef6cf))
* ensure summoned ring_and_bolt operator reverts back to previous values on cancel ([4dbc91c](https://github.com/hugemenace/nd/commit/4dbc91c51d6eda5f41ce47abf21edf426c792520))
* fix solidify operator weighting label array index error ([f3eabc8](https://github.com/hugemenace/nd/commit/f3eabc8dab22e5b6b9199c0300fefa56e37e7d81))
* remove unneeded viewport cursor wrap behaviour ([26a14c6](https://github.com/hugemenace/nd/commit/26a14c63320df2efb0eda4210f8e2488a26d7e05))

## [1.5.0](https://github.com/hugemenace/nd/compare/v1.4.0...v1.5.0) (2022-02-06)


### Features

* add screw head generator ([c91ac08](https://github.com/hugemenace/nd/commit/c91ac08220824ada9b6f7dfd1c43e24ff7775dec))
* add toggleable "halt" mode to all operators, allowing event / keybinding passthrough ([1ec0942](https://github.com/hugemenace/nd/commit/1ec0942a279607a130fa3165dab36aec039b7c0a))


### Bug Fixes

* add planar decimate modifier to ring_and_bolt objects if the segment count is greater than 3 ([d92dc02](https://github.com/hugemenace/nd/commit/d92dc02724bea7eb411596fca42047a51cb6bc22))

## [1.4.0](https://github.com/hugemenace/nd/compare/v1.3.0...v1.4.0) (2022-02-04)


### Features

* add utils menu as sub-menu on main menu ([2d88ed2](https://github.com/hugemenace/nd/commit/2d88ed284c5246cad9cca43483988466bc2bdff8))

## [1.3.0](https://github.com/hugemenace/nd/compare/v1.2.1...v1.3.0) (2022-01-31)


### Features

* add a dynamic relationship between inner radius and width parameters, for more predictive results, and better ring generation ([03b15f6](https://github.com/hugemenace/nd/commit/03b15f6bf2d313581fcbfe21d859d850393e9adc))


### Bug Fixes

* enforce 0.0001 minimum width for weighted normal bevel, and add WN prefix to bevel modifier name for better recognition ([2831254](https://github.com/hugemenace/nd/commit/2831254258916f1143e9246a7bb1efdea5c3411a))

### [1.2.1](https://github.com/hugemenace/nd/compare/v1.2.0...v1.2.1) (2022-01-30)


### Bug Fixes

* fix broken keymap entry property name for main menu after name change ([3cf72cb](https://github.com/hugemenace/nd/commit/3cf72cb2a8339764263d6e1d1fc30657cc607905))
* use more reliable collection objects link call for operators creating single vertex objects ([58d433a](https://github.com/hugemenace/nd/commit/58d433aea8242ae2a629f7750b4c9d09df80b378))

## [1.2.0](https://github.com/hugemenace/nd/compare/v1.1.1...v1.2.0) (2022-01-30)


### Features

* add name_sync operator and new ND Utils UI panel ([dfcc13d](https://github.com/hugemenace/nd/commit/dfcc13d72f422df27de1eb4fe7ba0eae5f0d11bf))
* add set_lod_suffix operator ([3e9cdb1](https://github.com/hugemenace/nd/commit/3e9cdb16be816b797a90f9ceeda3ba79ac794cf5))
* allow F key passthrough on face_sketch operator ([a8e4e3a](https://github.com/hugemenace/nd/commit/a8e4e3a88545d487a38f56f61f48110594460e74))


### Bug Fixes

* clear custom split normals on extracted faces in face_sketch operator ([f33ac67](https://github.com/hugemenace/nd/commit/f33ac673496afbe60f2b11a2ae4a497b744f5aaa))
* ensure clean up method in face_sketch operator removes extracted face when the operation is cancelled ([17cb5e1](https://github.com/hugemenace/nd/commit/17cb5e1c19840481074b06f25ef0288b3604c955))
* fix incorrect class name unregister call in main_menu.py ([b11a97b](https://github.com/hugemenace/nd/commit/b11a97b8bbe6947276e33c0de915ef9a57ba0e59))
* fix poll method qualifier in name_sync operator ([8c5f585](https://github.com/hugemenace/nd/commit/8c5f5850ad3b062a38b75d6e4d7e0132e18d8048))
* set the bevel modifier offset type to 'width' for the vertex_bevel, and weighted_normal_bevel operators ([9b561aa](https://github.com/hugemenace/nd/commit/9b561aa4745009894043d3e1fb0eec3543df576a))

### [1.1.1](https://github.com/hugemenace/nd/compare/v1.1.0...v1.1.1) (2022-01-29)


### Bug Fixes

* add missing capture_modifier_keys function call to invoke method on face_sketch operator ([573d0d2](https://github.com/hugemenace/nd/commit/573d0d2c8246001b68512aecd7d9cc133e660d14))
* remove hardcoded mm suffix on all operator overlay parameter labels ([c5a253e](https://github.com/hugemenace/nd/commit/c5a253ef59ed262c1fc378b22adaa21b65ef87f8))
* set starting width parameter to 0 on vertex_bevel operator ([130f8ef](https://github.com/hugemenace/nd/commit/130f8ef2d941d023e24dd3a310e68c961c2d5dd0))

## [1.1.0](https://github.com/hugemenace/nd/compare/v1.0.0...v1.1.0) (2022-01-29)


### Features

* add face extraction mode to view_align operator and rename it to face_sketch, rename new_sketch to blank_sketch, and sketch_bevel to vertex_bevel ([2a04917](https://github.com/hugemenace/nd/commit/2a04917434605c20c5264c188b7c1b5acb2164a6))
* rename operators - spinner to screw, thickener to solidfiy, and faux_bevel to weighted_normal_bevel ([c7e4d2c](https://github.com/hugemenace/nd/commit/c7e4d2c14466151aa5b6607087cf318da02f28f7))
* split offset and thickness modifiers from bolt operator in favour of solidy operator usage, add ring functionality to bolt operator, rename bolt to ring_and_bolt ([4585823](https://github.com/hugemenace/nd/commit/4585823c4093102c3df0d93f99f79fe104902012))


### Bug Fixes

* add invalid face selection error handling for face_sketch operator ([32a491a](https://github.com/hugemenace/nd/commit/32a491a4ac374e74eadf7c78a86e22fc1bdcf104))
* ensure update_overlay function is called after every event type ([c5d59b0](https://github.com/hugemenace/nd/commit/c5d59b091d73702bc648511459574812136cab16))
* fix ring_and_bolt parameters and parameter names to more appropriately represent their behaviour ([6ee7a6b](https://github.com/hugemenace/nd/commit/6ee7a6bee3d0c1576104df8dc4bacff9d06f6018))
* update solidify weighting parameter name ([5586b69](https://github.com/hugemenace/nd/commit/5586b6981d7314710aa602fa191867730f73c913))

## 1.0.0 (2022-01-28)


### Features

* add __init__.py with addon information ([77a92de](https://github.com/hugemenace/nd/commit/77a92deb218f1078e86046e0529ba0bc0bc342b4))
* add active and alt_mode key indicators to operator overlays ([bde234c](https://github.com/hugemenace/nd/commit/bde234ce47d319207c622325903712878bcab8f4))
* add custom HUD UI for all operators and allow viewport navigation event passthrough ([e032770](https://github.com/hugemenace/nd/commit/e032770664530ae59f8c749b8bf9664af2116c22))
* add initial menu ([a6329b3](https://github.com/hugemenace/nd/commit/a6329b3cb55c37f4c8a17c69555df8359b4d7bfc))
* add initial UI panel ([789f471](https://github.com/hugemenace/nd/commit/789f4715ee39aad893d2c0eddf36798eaa3b2867))
* add new_sketch operator ([3aca34b](https://github.com/hugemenace/nd/commit/3aca34bb96ceb836eb704a83223df85d02fa48f7))
* add overlay pinning option for all operators ([8bff7c4](https://github.com/hugemenace/nd/commit/8bff7c480cbca251e8e87191d5e2baaf4d886384))
* add spinner operator ([26c1aea](https://github.com/hugemenace/nd/commit/26c1aea60e47ae24b379a23989cf1eb301d72cb8))
* add spinner to UI panel and menu, reorganise operators, update icons ([bbc1002](https://github.com/hugemenace/nd/commit/bbc1002b11930d366c7befb6004068759432d7aa))
* add thickener modifier ([f215357](https://github.com/hugemenace/nd/commit/f215357a674f0c1abc5ec586d3202fcd7d23e014))
* add view alignment operator, and relatedly fix incorrect overlay redraw implementation — subsequently applied across all other operators ([7eabac6](https://github.com/hugemenace/nd/commit/7eabac6c3752afb8f2aad846094d8cc0e661498a))
* allow duplicate selection shortcut pass-through in new_sketch operator ([86255a0](https://github.com/hugemenace/nd/commit/86255a00717b49813c6fb5c9a0bf487706b36cbd))
* allow mm based factors to be scaled up and down on all operators ([c433400](https://github.com/hugemenace/nd/commit/c433400a215c51d49eb3b56a2b9d810a38187e38))
* create a dedicated overlay manager, drawing utilities, and update all operators respectively ([1520b36](https://github.com/hugemenace/nd/commit/1520b36caa328c69cbb98cea7271bb8a259ac0d1))
* ensure cutter bolts are clearly visible in the viewport, including their depth into the target ([d6d08f2](https://github.com/hugemenace/nd/commit/d6d08f2268c0997494dd13bcffa5d0b0a8997814))
* step bolt operator segments up by 2, and by 1 on shift, following similar operation to the sketch_bevel operator ([8dbece2](https://github.com/hugemenace/nd/commit/8dbece2e606f3ffe55072f4e8a3a07badf400584))
* unify input controls across all operators and add revert/cancel functionality ([5a79040](https://github.com/hugemenace/nd/commit/5a7904086860e2e5a27c3f378ec3ee350e3576ff))


### Bug Fixes

* add poll method to operators to ensure all conditions are correct before they can be invoked ([4faad28](https://github.com/hugemenace/nd/commit/4faad280d8c45fc382c7dcc4d89439a6c43ddbd7))
* add shade_smooth call to faux_bevel operator and remove legacy mouse_x/y variables ([0d994b7](https://github.com/hugemenace/nd/commit/0d994b70a4be68afef30ad21677551ea5def2cfe))
* add smooth shading step to faux bevel operator ([5f09d2c](https://github.com/hugemenace/nd/commit/5f09d2ca31f5bc6451bb016531b12a0734bead4f))
* ensure faux bevel weighted normal weight is set to 100% to avoid face-level artifacts ([0849dfd](https://github.com/hugemenace/nd/commit/0849dfd2a02cb53eb8595fd1a81fa2b5021c995d))
* ensure new sketches can only be created in object mode with no objects selected ([d77f839](https://github.com/hugemenace/nd/commit/d77f839470f4c1e7fcebba31ccf9f8f5e81ed9ea))
* ensure utils.set_3d_cursor handles the different possible cursor rotation modes ([b7100ec](https://github.com/hugemenace/nd/commit/b7100ec0fc6cc9758ecfeedc77736331ef64cac6))
* fix operator labels ([18023dc](https://github.com/hugemenace/nd/commit/18023dc885ebafd2842f0d611ab81389624757e7))
* fix register/unregister call for menu in __init__.py ([7683f8d](https://github.com/hugemenace/nd/commit/7683f8d35e1b7e3984e1f66fa1409e3722e77918))
* fix up file names and register all scripts from __init__.py ([94dd2b9](https://github.com/hugemenace/nd/commit/94dd2b9899444a7cc6a426949a2dbdfcab7cde30))
* set alt mode to constant False on segment property overlay of bolt operator ([99e4a12](https://github.com/hugemenace/nd/commit/99e4a1216a928e7b4dc22b3a57e503b27821f31b))
* set merge_threshold to 0.1mm for screw modifiers on bolt operator ([5d0c064](https://github.com/hugemenace/nd/commit/5d0c064041648e4127065e6b4b7afe1ad3135d62))
* standardize operator names ([c25991e](https://github.com/hugemenace/nd/commit/c25991e148df21cbff4bb209c7dda2bc1fca2135))
* update all operator, panel, and menu class names to follow Blender's naming convention and add execute method to operators for menu support ([86c96dd](https://github.com/hugemenace/nd/commit/86c96ddfe171b5aaa61a6c4ba17189fcc6081925))
