# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [1.28.1](https://github.com/hugemenace/nd/compare/v1.28.0...v1.28.1) (2022-05-27)


### Bug Fixes

* fix unexpected float error in Blender 3.1 and limit the possibility of dividing by zero errors on manual user input ([1cdac6c](https://github.com/hugemenace/nd/commit/1cdac6ce8718c947e6bcd93e545c6bbdf3494445))

## [1.28.0](https://github.com/hugemenace/nd/compare/v1.27.0...v1.28.0) (2022-05-27)


### Features

* add alt mode to vertex bevel to create a vertex group edge bevel ([77cfff4](https://github.com/hugemenace/nd/commit/77cfff4011993bebb0f0e38f5127a88a2b7b4677))
* add an option to custom default smoothing angle and update & add it across all relevant operators ([ed02679](https://github.com/hugemenace/nd/commit/ed026796f34e034c3ac471173fb69b9d0bcbb2dc))
* add apply_modifiers utility ([1ec0150](https://github.com/hugemenace/nd/commit/1ec01505c94df73051b8def906bd734a4e2492c3))
* add cycle operator to fast menu for objects with boolean modifiers present ([a71896c](https://github.com/hugemenace/nd/commit/a71896c6cea247d1c26b91b91a2b8b5c91dd1c4a))
* add decimate and weld operators under the new simplify menu ([1c7b454](https://github.com/hugemenace/nd/commit/1c7b454b3f47a2063f7a2745bea5d8b1094d443a))
* add edge angle limit option to bevel and weight_normal_bevel operators ([c44e0b1](https://github.com/hugemenace/nd/commit/c44e0b15e8be0ba091b0586216089cf4d6733bba))
* add enhanced wireframe mode toggle to all bevel operators ([03933cf](https://github.com/hugemenace/nd/commit/03933cf42b28d0e698385b14db7ee87e1315e879))
* add fast prediction menu ([eb26d59](https://github.com/hugemenace/nd/commit/eb26d59c9721c2c02753a095f8a7809834ca86f1))
* add flip normals option to screw operator ([768f1be](https://github.com/hugemenace/nd/commit/768f1beace3640311081a51fd88312d9ac35a1cd))
* add natural rotation option to recon poly ([980fde9](https://github.com/hugemenace/nd/commit/980fde980985d423559f0812c552d1c4852edc61))
* add option to place modifiers at the top/bottom of the stack across edge_bevel, vertex_bevel, and mirror ([fc08803](https://github.com/hugemenace/nd/commit/fc08803314309ca3805bff714a4dbe8ee186d3f9))
* add swap_solver utility ([5481109](https://github.com/hugemenace/nd/commit/548110999b0dde2c55429597bde8e049ddaddb0d))
* add the option to disable automatic update checks in preferences ([fbcb91d](https://github.com/hugemenace/nd/commit/fbcb91d1a2908b440a04fe490a13be359c2bccf3))
* allow for manual values to be supplied to overlay & optimise operator overlay options ([bffaf72](https://github.com/hugemenace/nd/commit/bffaf72e965906bbd2db7096d054f607832301bb))
* allow hydrate utility to be run on multiple selected objects ([12fc16e](https://github.com/hugemenace/nd/commit/12fc16e0e30ce85331c8a2ee73e92c4a0ede26ba))
* automatically move booleans under WN bevels and single segment HN bevels ([1170f08](https://github.com/hugemenace/nd/commit/1170f08495138a023961fc7b2b25c6a57b09df49))
* bind the fast menu to F and add a shortcut for Blender's underlying make edge/face operator ([b211a23](https://github.com/hugemenace/nd/commit/b211a2339fd23c25132ade2ccee6579c039c7ee3))
* improve the mod ordering logic and apply it to the weld and decimate modifiers ([5307ed0](https://github.com/hugemenace/nd/commit/5307ed052af1f1126d1ea3c7669ab319f51b7b90))


### Bug Fixes

* add a check to apply_modifiers for disabled modifiers and remove them instead of applying ([ffc655a](https://github.com/hugemenace/nd/commit/ffc655a4801487e187d5dd75e755f462f9396edf))
* add missing draw_hint import to edge_bevel operator ([7aec17d](https://github.com/hugemenace/nd/commit/7aec17d72acfd415b4dad3a8eed8defbed864ea7))
* display no prediction message when in edit mode and no precondition matches ([7154241](https://github.com/hugemenace/nd/commit/715424133c08f6e4eb3e2f8c60812909c3c22644))
* fix up has_mod_* logic in fast menu single object predictions ([3f27ee3](https://github.com/hugemenace/nd/commit/3f27ee31b19c4f36b012f23f7e86937d0be5d9be))
* fix weighting calculation in profile_extrude operator ([4cd46fb](https://github.com/hugemenace/nd/commit/4cd46fbbf2641255354c8930aad348431c379ae1))
* remove triangulate modifier & switch v3_average for .calc_center_median for face points in snap_align operator ([0842b3c](https://github.com/hugemenace/nd/commit/0842b3c5ac4fc7a2e413cb9d36917dd43b7117a6))

## [1.27.0](https://github.com/hugemenace/nd/compare/v1.26.0...v1.27.0) (2022-05-14)


### Features

* add Flare (Lighting) operator ([83e9be0](https://github.com/hugemenace/nd/commit/83e9be05a1dc794b07951999c6afbc2386e726f2))
* add option to automatically run solidify after a recon poly operation ([9a5dff3](https://github.com/hugemenace/nd/commit/9a5dff34ccaa7df329e4807bad51380568c2d497))
* add option to capture 2 points in snap_align to align the selected object at the midpoint ([21b7a0a](https://github.com/hugemenace/nd/commit/21b7a0a1236daf5216b88d9488799a5d5da0a8d8))
* add recall ability to circular_array operator ([1ff93e8](https://github.com/hugemenace/nd/commit/1ff93e8038287c22726383c7183cdf06735c0062))
* add snap_align operator ([7548c66](https://github.com/hugemenace/nd/commit/7548c6645449c2598dd3bd61f7a6555cb6176661))
* add temporary triangulation to active object during snap_align operations to increase face points ([640bc8c](https://github.com/hugemenace/nd/commit/640bc8cd52919b9d28925f4200394df8524b9f63))
* allow circular_array operator to be used on a single selected object, and alter origin/translation logic ([d273720](https://github.com/hugemenace/nd/commit/d273720c485ed053fa143fb047cdfa1bbdad9dc5))
* allow snapping to occur through objects occluding the target while using snap_align ([8301845](https://github.com/hugemenace/nd/commit/83018451e6af1b8e7acf25759175f62389df5bdc))
* enhance lattice modifier behaviour and allow it to be recalled ([10dc6f9](https://github.com/hugemenace/nd/commit/10dc6f985316f76c17adf2242e27bc1fc3d7468c))
* hide circular_array empties on completion and give them an appropriate name ([c04c466](https://github.com/hugemenace/nd/commit/c04c4664c021cdca75ba800ff6370ef637144b00))


### Bug Fixes

* ensure active boolean utils don't affect the geometry of the target object while using snap_align ([e796693](https://github.com/hugemenace/nd/commit/e7966936a9f9daeb6868e868bfa36d7de79b6b12))
* ensure guideline in snap_align operator is cleared when capture rotation is reset ([374ad50](https://github.com/hugemenace/nd/commit/374ad50f39b104f685e2e7184133024a6f9a54a4))
* ensure mirror selected object show_in_front mode is disabled on complete/cancel ([e2d0e07](https://github.com/hugemenace/nd/commit/e2d0e07dc9f81875f146aafe71f95da2b3137596))
* ensure simple deform angle decrements as intended using the step_down key event ([9e7b91a](https://github.com/hugemenace/nd/commit/9e7b91a355c8d751219e2bddfee06cc0045ff237))
* ensure snap_align operator supports meshes with vastly different edge lengths ([e9de396](https://github.com/hugemenace/nd/commit/e9de39678ee89aed01e26890dfdfcc7e029cdf85))
* ensure that the reference object is solo-selected when completing a snap_align operation ([73ff168](https://github.com/hugemenace/nd/commit/73ff16857a4422427023f797cf3bcdfdff0252ff))
* fix circular array revert behaviour for single object mode ([f14b5d2](https://github.com/hugemenace/nd/commit/f14b5d259a1ee6873a0af66d8880ca1edcf2ccb4))
* fix error when using cycle operator on objects with objectless booleans in their modifier stack ([d1bc6cf](https://github.com/hugemenace/nd/commit/d1bc6cf77ff38a8529784e8885a8a07907ca6bef))
* fix left-click handling for operators that need to pass through the event ([8a335b2](https://github.com/hugemenace/nd/commit/8a335b2e79f0da495f151085c5b21f832b315cd4))
* fix mirror over geometry empty's matrix parent inverse ([9a16503](https://github.com/hugemenace/nd/commit/9a1650387f3bb4ff9df575fac338fcee88e95caf))
* fix up circular_array and lattice overlay option control key labels ([22e7e54](https://github.com/hugemenace/nd/commit/22e7e54b9c10dbc324fa37b162c39908f1576b30))
* only detect click events on release when using interactive operators ([ee19d30](https://github.com/hugemenace/nd/commit/ee19d3059a98129772e51ef27a514af4128f3272))
* remove light energy offset limits ([1eb7964](https://github.com/hugemenace/nd/commit/1eb7964b9d3d051a116ded2740d7d14b5c81e3d4))

## [1.26.0](https://github.com/hugemenace/nd/compare/v1.25.0...v1.26.0) (2022-05-07)


### Features

* add enter & space key presses as additional operator finalisation events ([5e3eb6f](https://github.com/hugemenace/nd/commit/5e3eb6fc9e9bf7d9640c165b2127803821e79989))
* add modifier & utility cycle operator ([73bf7a3](https://github.com/hugemenace/nd/commit/73bf7a330e6ba90d30b7c0425dd1054ab7f0024e))
* add option to mirror across faces, edges, or vertices on selected object ([1ebc4ac](https://github.com/hugemenace/nd/commit/1ebc4acbc258415505e5a33fc0da86a87abc10ed))
* add shift option to vanilla boolean operator to protect reference object (do not convert into utility) ([9efae25](https://github.com/hugemenace/nd/commit/9efae2533b562402238ba3698f9d1983e07eb71b))
* add simple_deform operator ([d5acf67](https://github.com/hugemenace/nd/commit/d5acf6781349da0dfa2db33788d8278f8d037204))
* add triangulate modifier ([2e990f8](https://github.com/hugemenace/nd/commit/2e990f82ab56ebe850414648ff6725cbd298c215))
* allow for multiple utils to be selected with cycle operator ([8bb923b](https://github.com/hugemenace/nd/commit/8bb923bfc690edbb48a4302142ce0b0d9680084e))
* allow mirror modifier to be applied to multiple objects simultaneously ([80467d1](https://github.com/hugemenace/nd/commit/80467d1b573b14c96f0a763edb6037b33e2fee51))
* automatically set geometry mirror axis to Z and flipped ([426ed79](https://github.com/hugemenace/nd/commit/426ed79fefe25d296b25ccde165254215d5e57bd))
* move sketch operators into their own sub-menu ([08bb8fd](https://github.com/hugemenace/nd/commit/08bb8fd04c19775d5623f522190423cb2083152a))
* tidy up main menu by creating Replication and Deformation sub menus to house appropriate operators ([6cf9461](https://github.com/hugemenace/nd/commit/6cf9461a7623eb0b03f8b4a49f1380dd40a96afb))


### Bug Fixes

* ensure boolean operators isolate the reference object in the utils collection ([14dfdf4](https://github.com/hugemenace/nd/commit/14dfdf4887cac99aaa11c80e17e21ca80dfe0b5a))
* ensure mirror empty object is removed if mirror operator is cancelled after geometry selection ([9c13ab6](https://github.com/hugemenace/nd/commit/9c13ab696b1843c1ea3b9d25754fcb1dd01fee01))
* fix alt key value change behaviour on cycle operator ([9efadc8](https://github.com/hugemenace/nd/commit/9efadc8ac31c9b708a0c0204e296b002cfdfe89c))
* fix geo_lift operator event handling order ([447c654](https://github.com/hugemenace/nd/commit/447c65453ad7e34e06f231cd9e3274ed49c775e8))
* fix recon poly width option overlay display value ([8413096](https://github.com/hugemenace/nd/commit/841309665466bee5738d6aa5995431fba41dbc48))
* fix reference/target object parenting in circular_array operator ([7df4058](https://github.com/hugemenace/nd/commit/7df4058928d6a5fd717715e14def436565e6e9de))
* fix up mirror across geometry invalid selection cleanup logic ([97873a4](https://github.com/hugemenace/nd/commit/97873a4c59b3ab36b890feecdfff6876a076cb31))
* update set_lod_suffix mode type in utils_menu ([73aa1e7](https://github.com/hugemenace/nd/commit/73aa1e7ee9a172e1613d3630759c4cf7070baeae))

## [1.25.0](https://github.com/hugemenace/nd/compare/v1.24.0...v1.25.0) (2022-04-29)


### Features

* add clear vertex groups utility ([ef5e5d5](https://github.com/hugemenace/nd/commit/ef5e5d50362f44091d1b44a0418e333d19a907f4))
* add isolated vertices in selection to active group in vertex bevel recall ([b62c55c](https://github.com/hugemenace/nd/commit/b62c55c5ba372840efe0e9074209ab881dadef07))
* add recall functionality to vertex bevel operator ([7b5cd83](https://github.com/hugemenace/nd/commit/7b5cd83d1a03273dc79b1438fd4a89debc49fb18))
* add shortcut for isolated utils menu ([dcfdf35](https://github.com/hugemenace/nd/commit/dcfdf354892268f407258cc83918f274caa67f65))


### Bug Fixes

* fix circular array revert behaviour ([0d61d74](https://github.com/hugemenace/nd/commit/0d61d74db3187f1af8924884da380cbcaf41924c))
* match target object rotation in circular_array operator ([7ea17b0](https://github.com/hugemenace/nd/commit/7ea17b04faa216a79b9c2f32a522eae314938738))
* remove set rotation from faux set_origin ([e371881](https://github.com/hugemenace/nd/commit/e37188103b0317b6190cc0a961a0b0cc0c725526))
* replace center of volume with bounding box calculation in lattice operator ([22add82](https://github.com/hugemenace/nd/commit/22add821f7383c6542f15dcbdd28bd70268260f9))

## [1.24.0](https://github.com/hugemenace/nd/compare/v1.23.0...v1.24.0) (2022-04-26)


### Features

* add alt mode to geo_lift operator to ignore all bevels when calculating selectable geometry ([2aff5bc](https://github.com/hugemenace/nd/commit/2aff5bcda7a3f65b375f3de1863eb953f50c9d88))
* add bool_inset operator ([3f29af5](https://github.com/hugemenace/nd/commit/3f29af5a23f95bb7a73bef4ed8753d756aae297f))
* add edge_bevel operator ([9d876f4](https://github.com/hugemenace/nd/commit/9d876f487ca3936e472e739cd7b6b7276cfd2bac))
* add harden normals option to vanilla bevel operator ([7827900](https://github.com/hugemenace/nd/commit/7827900651e3b08ec940176919a692e64d21f874))
* add lattice operator ([fd6eae0](https://github.com/hugemenace/nd/commit/fd6eae0171070a16161c1ea1f19735e98998ca2b))
* add mode option shortcut key for bool_inset operator ([5fc4d30](https://github.com/hugemenace/nd/commit/5fc4d3008caa1710f49385a869e36d0ce8d6ede9))
* add option to lock overlay pin state and position across all operators ([0ce0dd7](https://github.com/hugemenace/nd/commit/0ce0dd71024647acf4165757d8bdcff7042d79ee))
* add outset mode to bool_inset operator ([cc8edd7](https://github.com/hugemenace/nd/commit/cc8edd7fd842569f427aa91c434a8adc7e18b651))
* add toggle option shortcut keys to applicable operators ([c10b066](https://github.com/hugemenace/nd/commit/c10b066220dbd8789f27a368527cffa1c441d63a))
* add traditional (now default) and faux origin translation to set_origin utility ([5122bae](https://github.com/hugemenace/nd/commit/5122bae4640e48c6dd5f3b514353dd78600e5657))
* allow for -360 degree rotation on screw operator ([306a3e2](https://github.com/hugemenace/nd/commit/306a3e2be6d8a98b78cb8361cf8c16bf64f88947))
* set face strength mode and face influence on wn_bevel modifiers ([eb7cd25](https://github.com/hugemenace/nd/commit/eb7cd2594198e19b77212d5b75f3924032e51a72))


### Bug Fixes

* add additional checks to all operator poll methods to avoid selection (and order) based errors ([cfdde4c](https://github.com/hugemenace/nd/commit/cfdde4c3ce3deaad5c2d2a7577b13ac1b9d20cc6))
* ensure circular_array operator allows for traditional (now default) and faux origin translation ([a21a46c](https://github.com/hugemenace/nd/commit/a21a46c6be4e73bdbe47707f7d77d236ebe52f55))
* remove all ND menus from info header bar ([db17157](https://github.com/hugemenace/nd/commit/db17157635611f6d0ef030fa8a1ca63442842838))
* set miter_outer to arc in bevel operator ([fc4420b](https://github.com/hugemenace/nd/commit/fc4420b72b1a2dd0d2e52e303578153a6fe2b4bd))

## [1.23.0](https://github.com/hugemenace/nd/compare/v1.22.0...v1.23.0) (2022-04-22)


### Features

* allow array_cubed count to roll faux negative ([9138c66](https://github.com/hugemenace/nd/commit/9138c665ec00fb62a24b9664e1f5d2008fb0b47c))
* distinguish between built-in and custom screw head types in the operator overlay, and add additional .blend file cleanup on revert ([a37a5bf](https://github.com/hugemenace/nd/commit/a37a5bfc0986dcab7f1cb5b70c88dd26044703d8))

## [1.22.0](https://github.com/hugemenace/nd/compare/v1.21.0...v1.22.0) (2022-04-22)


### Features

* add array_cubed operator and deprecate square_array ([d90dec6](https://github.com/hugemenace/nd/commit/d90dec6471c75977f5b279d3ff0b0f5e17bd0809))
* add custom screw heads (.blend file) option to addon preferences ([539d982](https://github.com/hugemenace/nd/commit/539d982e34b8de4d47a196d57b4fc6feb162672b))
* add enhanced axis visualization to array_cubed, mirror, profile_extrude, and screw modifiers ([9d2cd74](https://github.com/hugemenace/nd/commit/9d2cd74b3d844857dafe294576cd215b30812852))
* add toggle for "fast" booleans in addon preferences and set default to true (previously "exact") ([43afa87](https://github.com/hugemenace/nd/commit/43afa87c5662f3a1ff7ca88d087c43834e9858df))
* allow circular_array operator to be run on objects, empties, and at arbitrary rotations ([45cb48b](https://github.com/hugemenace/nd/commit/45cb48b196cbd35a09ef02f8280a79eebb1581ac))
* show axes on selected object when using the array_cubed operator ([77a2a85](https://github.com/hugemenace/nd/commit/77a2a8569f0404ee6f2f7324b0214ff3afb7099d))


### Bug Fixes

* match target object rotation in set_origin operator ([09da9e8](https://github.com/hugemenace/nd/commit/09da9e8750d49dbf462fac47f1e19e4207219c96))

## [1.21.0](https://github.com/hugemenace/nd/compare/v1.20.1...v1.21.0) (2022-04-18)


### Features

* add mouse values mode, and integrate all applicable operators ([a873f74](https://github.com/hugemenace/nd/commit/a873f7455d2a6310d4a29b3231336cdb25203e5c))
* add profile option to vanilla bevel operator ([ca24b38](https://github.com/hugemenace/nd/commit/ca24b382d708a4618377f5a7a40498a2bb111ec5))


### Bug Fixes

* ensure a weld modifier is placed after a vanilla bevel modifier ([5cecea6](https://github.com/hugemenace/nd/commit/5cecea6ece0a8cc49b73128218143cdbe0333273))
* ensure the previous profile value is retained when summoning & reverting a vanilla bevel operator ([733f6ad](https://github.com/hugemenace/nd/commit/733f6ad0f65fb4ae1bb77d0a15502fb4de6b39a3))
* fix profile option behaviour on vertex_bevel operator ([9f22e77](https://github.com/hugemenace/nd/commit/9f22e7747b716c3ebcfd94f1e3f7efbc1aa0d8b9))
* swap width and segments options on vertex_bevel operator to align with vanilla bevel operator ([c9c7e6b](https://github.com/hugemenace/nd/commit/c9c7e6bdb6324b7ec97cc966ee04f5f6831306ce))
* update recon_poly option ordering to better align with other operators (width > segments > etc.) ([4c107e9](https://github.com/hugemenace/nd/commit/4c107e99b07600f414e2e9b862cac1a9093fc38a))

### [1.20.1](https://github.com/hugemenace/nd/compare/v1.20.0...v1.20.1) (2022-04-17)


### Bug Fixes

* ensure all scene objects are deselected before executing core single_vertex operator functionality ([43b4e6d](https://github.com/hugemenace/nd/commit/43b4e6d4ced4fbbc2d116c399d0768c485e968fe))

## [1.20.0](https://github.com/hugemenace/nd/compare/v1.19.0...v1.20.0) (2022-04-17)


### Features

* allow customization of overlay pin and pause keybinds ([aae7e91](https://github.com/hugemenace/nd/commit/aae7e91c667cc8ea7b05586b5cebe1c89bfa1706))
* organise addon preferences panel and expose Blender keymap settings ([35c26bb](https://github.com/hugemenace/nd/commit/35c26bba1e77b5cd401af8d45dddde6b65cf0eec))
* split blank_sketch into single_vertex and make_manifold operators ([08f6efe](https://github.com/hugemenace/nd/commit/08f6efefeee9de51e24c1945b12d91d8664ac625))


### Bug Fixes

* fix incorrectly labled profile_extrude overlay alt/ctrl key options ([8134622](https://github.com/hugemenace/nd/commit/81346226fc9607525a7029aa5aa48feb9cd13efc))

## [1.19.0](https://github.com/hugemenace/nd/compare/v1.18.0...v1.19.0) (2022-04-12)


### Features

* add hydrate operator ([a4aef0f](https://github.com/hugemenace/nd/commit/a4aef0f8337d78c5d761e1fca3690a22d44a9ea2))
* add option to enable quick favourites on primary menu ([1e8805d](https://github.com/hugemenace/nd/commit/1e8805de77e6277a45063c283a6eb456486a6bd5))
* add optional late-invocation mode to vertex bevel operator (for post-sketch usage) ([ff0ffa4](https://github.com/hugemenace/nd/commit/ff0ffa46016bbfe5d1db6047568b0f06389023c0))
* add ortho_grid to toggle_clear_view operator ([5e4f8de](https://github.com/hugemenace/nd/commit/5e4f8defc01ff75fe60e9049586cd3f70919153c))
* add viewport menu (with various initial toggles) ([1d09367](https://github.com/hugemenace/nd/commit/1d09367805d3d2f76cb27da6a0fd70ef8cb65661))
* automatically place boolean reference and circular array rotator objects in a utils collection (name configurable in preferences) ([eece58b](https://github.com/hugemenace/nd/commit/eece58bddd1dee663cfb95b03b3f07802e47c065))


### Bug Fixes

* ensure all objects in utils collection are toggled along with the collection consistently ([1316fff](https://github.com/hugemenace/nd/commit/1316fff82b2760ee80ede886342fc1f65bf15669))
* fix object visibility error in toggle_utils_collection operator ([52f3ada](https://github.com/hugemenace/nd/commit/52f3ada8b2facd3f341e4387ed2db2a7a6ee8818))

## [1.18.0](https://github.com/hugemenace/nd/compare/v1.17.0...v1.18.0) (2022-04-09)


### Features

* add square_array operator and create arrays sub-menu ([14ea44e](https://github.com/hugemenace/nd/commit/14ea44e7cdaa471fcecc7d453ac0eed89bce9d59))
* allow active overlay values to be updated with arrow and WASD keys ([dbb30c9](https://github.com/hugemenace/nd/commit/dbb30c94e0ec9dba795881b4ab6a54dc02605baa))


### Bug Fixes

* ensure ND keymap is included in 3D View, Mesh, and Object Mode by default ([95498b1](https://github.com/hugemenace/nd/commit/95498b18c602617196221c97fb57aa80c05f601b))

## [1.17.0](https://github.com/hugemenace/nd/compare/v1.16.0...v1.17.0) (2022-04-05)


### Features

* add a message/button to the shortcut menu & a link to the changelog in the UI panel when an update is available ([bd754cb](https://github.com/hugemenace/nd/commit/bd754cbd11729b9534dbf89e6dfff150eebb64a6))
* add bevel operator ([126af0d](https://github.com/hugemenace/nd/commit/126af0d7311576c3dfff6bc8429fdcf03bae078b))
* add circular_array operator ([8d6d20e](https://github.com/hugemenace/nd/commit/8d6d20eb21d6a73370a0770342bedbc1539d5177))
* adjust circular array option order, add even/odd count step, and allow negative arc angles ([b9dedf0](https://github.com/hugemenace/nd/commit/b9dedf0ea1f699da8c8a3755be402d268b2b9558))
* ensure mirror modifier bisects selected axis & add flip option for negative axis mirroring ([10ddb3d](https://github.com/hugemenace/nd/commit/10ddb3d5c8cf1b777f18835e4e978e35444e8863))
* organise operators by relevance in the shortcut menu ([b450ba9](https://github.com/hugemenace/nd/commit/b450ba9b75a615cc074db5fd1be44aa2eda93d5b))
* update documentation section on main UI panel & add Discord link ([b5c2d0f](https://github.com/hugemenace/nd/commit/b5c2d0fcd701d0ab90e12c859a0b1ed868cf854b))


### Bug Fixes

* ensure operate is only executed on interactive option mutation ([8fa29fc](https://github.com/hugemenace/nd/commit/8fa29fc01e93daae2afd88a5aa7d38a63a966e2e))

## [1.16.0](https://github.com/hugemenace/nd/compare/v1.15.0...v1.16.0) (2022-04-03)


### Features

* add overlay DPI control to preferences ([479710b](https://github.com/hugemenace/nd/commit/479710b47543791d51326a7f8a0cfc3f53f13724))


### Bug Fixes

* ensure overlay option precision mode indicator is inactive when in pause mode ([55ed7ba](https://github.com/hugemenace/nd/commit/55ed7baaa32c52a9a7eef5e16680034c138c0e24))
* ensure that the screw operator calculates the order of edges for correct normals ([a991db7](https://github.com/hugemenace/nd/commit/a991db74e1cd8239b8c950ba1d70e9365bfa6501))

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
