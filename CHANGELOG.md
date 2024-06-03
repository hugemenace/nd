# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [1.43.0](https://github.com/hugemenace/nd/compare/v1.42.0...v1.43.0) (2024-06-03)


### Features

* add an option in general preferences to toggle auto smoothing across all operators ([2d80d10](https://github.com/hugemenace/nd/commit/2d80d10aba1f385594c11add4a838b80e37a7e42))


### Bug Fixes

* fix version number check when check for updates is enabled ([83027b8](https://github.com/hugemenace/nd/commit/83027b84531194ace3f017d9c3276a7e8e355d6c))

## [1.42.0](https://github.com/hugemenace/nd/compare/v1.41.2...v1.42.0) (2024-05-25)


### Features

* add a hard apply & duplicate mesh alternative mode to the apply modifiers operator ([7132c12](https://github.com/hugemenace/nd/commit/7132c12252110a27494b4ed0b7398b04967bcf2a))


### Bug Fixes

* fix the incorrect object position offset when reversing a faux origin displacement ([e601e43](https://github.com/hugemenace/nd/commit/e601e43e345a4a9e0a50108d5639e25784dda5ba))

### [1.41.2](https://github.com/hugemenace/nd/compare/v1.41.1...v1.41.2) (2024-05-08)

### [1.41.1](https://github.com/hugemenace/nd/compare/v1.41.0...v1.41.1) (2024-05-07)


### Bug Fixes

* fix Blender 4.2 extension compatibility issues ([08004b7](https://github.com/hugemenace/nd/commit/08004b732cb8733ccc52fdf2efc7fb4c6a135172))

## [1.41.0](https://github.com/hugemenace/nd/compare/v1.40.0...v1.41.0) (2024-04-15)


### Features

* add an option to toggle the visibility of utils for only the selected objects ([d06cea6](https://github.com/hugemenace/nd/commit/d06cea69d0ad19bbc3ff3e5784d676ad66149242))
* add robertson, torx tamper proof, and triangle recess screw head types ([98e7fd1](https://github.com/hugemenace/nd/commit/98e7fd16a84006539db5ffa13ea83183ccb3cfda))


### Bug Fixes

* ensure that boolean ops handle the presence of WN mods correctly ([fff5894](https://github.com/hugemenace/nd/commit/fff5894b291324bf1ca630e3b73f160b0086e532))
* ensure that the SBA and WN mod order is maintained when new mods are added to the stack ([e8f8c7e](https://github.com/hugemenace/nd/commit/e8f8c7ef6fbf9da735f24c6c1fca2fa74bf80572))
* ensure that the WN modifier doesn't add additional mods to an object with the WN mod already applied ([c1b9607](https://github.com/hugemenace/nd/commit/c1b960737a825b3c3bfbe345686df2777a20aa2d))
* ensure the SBA mod places itself before any WN mod present in the stack ([c562b27](https://github.com/hugemenace/nd/commit/c562b277cf79aa3db9f022c62772debb28804b1e))
* fix NoneType error and add additional guard clauses for when the active target object is excluded from the view layer ([322c4bd](https://github.com/hugemenace/nd/commit/322c4bdea91faea91ab315da8b8fc69259bde488))
* fix smoothing mod removal error on profile extrude when cancelling a new (non-recalled) operation ([839c75c](https://github.com/hugemenace/nd/commit/839c75c4bd5bac073c968bfaccc31be1ac7f38b0))

## [1.40.0](https://github.com/hugemenace/nd/compare/v1.39.1...v1.40.0) (2024-03-22)


### Features

* add right-click select support (toggle via add-on preferences) ([7e7aad4](https://github.com/hugemenace/nd/commit/7e7aad4d0ac46041fa76a4afb3689fa5a5d73fa8))
* add support for Blender 4.1's new smoothing process ([316ecdc](https://github.com/hugemenace/nd/commit/316ecdca0d0ebe5cfc295f27aa9068bcde47fcac))


### Bug Fixes

* fix circular array empty rotation in single-object mode and tidy up operator ([e39bfc1](https://github.com/hugemenace/nd/commit/e39bfc199136e2fff2623370647a6d0b39b3c6a7))
* fix lattice scaling in Blender >= 4.1 ([14bf1aa](https://github.com/hugemenace/nd/commit/14bf1aa973df9f98d6ba48a07c9d2d36a5acfd2b))

### [1.39.1](https://github.com/hugemenace/nd/compare/v1.39.0...v1.39.1) (2024-02-24)


### Bug Fixes

* [Blender 4] fix an error when hydrating cutter utilities with the clear-parent option selected ([3fb0b05](https://github.com/hugemenace/nd/commit/3fb0b058e1b1eff197b81b07c75784cda218e765))
* [Blender 4] fix an error when mirroring an object with the SHIFT (place on top of the stack) alt-mode selected ([49d5e38](https://github.com/hugemenace/nd/commit/49d5e38c62f2d145b253cdd6fb23857ceb003524))
* ensure that hydrated object names do not include additional leading spaces ([7a41891](https://github.com/hugemenace/nd/commit/7a418911d9b3a992f70a9fce53e205861e4c11a0))
* ensure that the clear parent behaviour on hydrated utils does not clear the initially selected object(s) ([8f9f69f](https://github.com/hugemenace/nd/commit/8f9f69fff15271e53b723d72155951fe453799cd))

## [1.39.0](https://github.com/hugemenace/nd/compare/v1.38.0...v1.39.0) (2024-02-03)


### Features

* add the option to stack bevel modifiers, and cycle through stacked bevels when recalling ([41ba743](https://github.com/hugemenace/nd/commit/41ba7435703e572f27291b24744e9b4579d75ec0))


### Bug Fixes

* ensure that the edge.index exists in the edges_snapshot before reverting an edge bevel operation ([8b15a57](https://github.com/hugemenace/nd/commit/8b15a571609e43083e7b72fa44928bf821503909))

## [1.38.0](https://github.com/hugemenace/nd/compare/v1.37.0...v1.38.0) (2023-12-01)


### Bug Fixes

* fix additional Blender 4 compatibility issues ([2ffe4af](https://github.com/hugemenace/nd/commit/2ffe4afa743722d058921915457ffdcd6573aa9e))
* fix Blender 4 compatibility issues ([6c25e01](https://github.com/hugemenace/nd/commit/6c25e013c01cd950e4b4881fdc81bde7b2d60a4e))
* fix Blender 4 shader issues for Axis and Point visualisation ([460d2a3](https://github.com/hugemenace/nd/commit/460d2a3ae243af0528f2ac8d26b80a83019ec1fb))

## [1.37.0](https://github.com/hugemenace/nd/compare/v1.36.1...v1.37.0) (2023-07-14)


### Features

* add an apply modifier option to the cycle operator ([33a035a](https://github.com/hugemenace/nd/commit/33a035acab0aa072f0b0079caf6b349253c72d43))
* add keymaps for difference, union, intersect, and slice boolean operations ([402857d](https://github.com/hugemenace/nd/commit/402857d82b2149a3a3bb36525b215fe6047618c9))
* add loop slide and clamp overlap options to the edge bevel modifier and swap the weight and width options ([7747f33](https://github.com/hugemenace/nd/commit/7747f33a1fc8c95e1933d0577a6d518f4bd26569))
* add only ngons option to triangulate modifier ([1a8221b](https://github.com/hugemenace/nd/commit/1a8221b11147bac8c66f3ae60cf9d504fd6ce6a7))
* add support to high/low LOD for ZenSet's object naming convention ([074f2ff](https://github.com/hugemenace/nd/commit/074f2ff2c6653318ff5bc46e2545d86d6e15ab62))
* remove the WN bevel operator and update the standard bevel and weighted normal operators so that the functionality can be replicated ([3e55ba0](https://github.com/hugemenace/nd/commit/3e55ba0eb7a5cf07c4c4d5fc845074dc624d788b))
* set the angle parameter on the bevel operator as a mouse-driven value ([8d059c4](https://github.com/hugemenace/nd/commit/8d059c4bc21ced68533c265f9bc73115d7c5a96c))


### Bug Fixes

* fix the edge bevel operator's width and weight hints ([ab7e3f4](https://github.com/hugemenace/nd/commit/ab7e3f49ebc12bf63693a689163b26b419ea3cf6))

### [1.36.1](https://github.com/hugemenace/nd/compare/v1.36.0...v1.36.1) (2023-02-06)


### Bug Fixes

* fix error in panel operator after geometry selection ([55b6250](https://github.com/hugemenace/nd/commit/55b62501ffb025cd08b09623cede3d5c43a2ffc2))

## [1.36.0](https://github.com/hugemenace/nd/compare/v1.35.0...v1.36.0) (2023-01-31)


### Features

* add adaptive unit fallback support for both metric (meters) and imperial (feet) ([23435b4](https://github.com/hugemenace/nd/commit/23435b4c1d3f54ad185390993ea9e544007911f1))
* add constant displacement mode option to array_cubed operator ([5a79e34](https://github.com/hugemenace/nd/commit/5a79e3482b822b3d77576f7543465ebc5b81420c))
* add full support for Blenders unit system (None, Metric, and Imperial) and unit scales ([456ddc4](https://github.com/hugemenace/nd/commit/456ddc4d094db82eb63b9e1f99420911e3af1517))
* add mouse-value support to all non-keybound operator options ([99b21a6](https://github.com/hugemenace/nd/commit/99b21a68e3790452b845185aa2fda9fe40d3660c))
* add scene unit scale support for operator overlay values ([f9b8368](https://github.com/hugemenace/nd/commit/f9b83686ac130af1d7627d95e2c2f81d5f17e577))
* add silhouette operator ([f8ea2a3](https://github.com/hugemenace/nd/commit/f8ea2a3e6c9d7f31a20d7f087cf38b66ee119b59))


### Bug Fixes

* add fallback support for Blender's "Adaptive" unit length (default to meters) ([2443f0e](https://github.com/hugemenace/nd/commit/2443f0ee68834f4fa254f5d45f96caac07e52968))
* ensure object names with multiple chained ".00n" suffixes are fixed before high and low LOD naming operations ([872fb09](https://github.com/hugemenace/nd/commit/872fb090f76562355bcc7b3f8f01f2018dee550d))
* fix screw head z-axis displacement issue when altering scale ([f3340c1](https://github.com/hugemenace/nd/commit/f3340c12b643c33cd4b57179deb08a5d41aea53c))
* fix XYZ axis visualisation extents ([0b61363](https://github.com/hugemenace/nd/commit/0b61363ff8c3f608c14d4ee695c8da1d55d09557))
* set weld mode to connected for all bevel operators ([9b9d7d8](https://github.com/hugemenace/nd/commit/9b9d7d8ab4a6df02a0bda0793f28f12c3bdd3932))

## [1.35.0](https://github.com/hugemenace/nd/compare/v1.34.0...v1.35.0) (2022-11-05)


### Features

* add circularize operator ([722a14a](https://github.com/hugemenace/nd/commit/722a14aee4f7075ef95f5e6e89b6c1838293c1d8))
* add clamp_overlap and loop_slide options to bevel operator ([3f72296](https://github.com/hugemenace/nd/commit/3f722961f99e3574e63f4d62260403233ca6f201))
* add decimate modifier to circularize operator and set min segments to 2 ([d08f5bc](https://github.com/hugemenace/nd/commit/d08f5bcad833a8790c3f6c09a2c4d02430888fd4))
* add immediate apply mode to seams operator, default to angle set in preferences, and lock auto smooth to 180 degrees ([ad2b167](https://github.com/hugemenace/nd/commit/ad2b167b15c08b7d51010ab2e549207e06fb30f8))
* add mesh mode set_origin behaviour ([f116a8d](https://github.com/hugemenace/nd/commit/f116a8d052ac5f29b35a13f84cf709f88ef394f3))
* add the circularize operator as a fast menu PE/sketch prediction ([3b89d57](https://github.com/hugemenace/nd/commit/3b89d57775ced86b1c343d66807c42502b1b5096))


### Bug Fixes

* add edge_bevel and overlay fixes for Blender 3.4 ([2700e23](https://github.com/hugemenace/nd/commit/2700e2357f73adf5eaf3b7efcabd27e4b4761c41))
* add overlay_option_active_color back into reset_theme operator ([4cbc00b](https://github.com/hugemenace/nd/commit/4cbc00b0f8f7b6e95bb8c1fb5b9ecaf1aee8878c))
* ensure vertex groups and edge weights are remove when applying modifiers ([587c2af](https://github.com/hugemenace/nd/commit/587c2af52f4a80ceece33b9662a27ef3efd68b3d))
* fix profile_extrude and solidify normal calculations ([3ded508](https://github.com/hugemenace/nd/commit/3ded508bf018c2d3bcc28dfd5a7b9bfee46671d5))
* only apply viewport visible modifiers ([8b7b7c2](https://github.com/hugemenace/nd/commit/8b7b7c203d5d11280b2569d1090c67ee86039545))
* register recon_poly segments with mouse values system ([64929d4](https://github.com/hugemenace/nd/commit/64929d40e258f965a2f1686466ed97ee81faaccb))

## [1.34.0](https://github.com/hugemenace/nd/compare/v1.33.0...v1.34.0) (2022-09-19)


### Features

* add a bulk assign ID materials operator ([fc3a4c6](https://github.com/hugemenace/nd/commit/fc3a4c671285bef41696b37fd2894aa5cb185ae3))
* add a weighted_normal operator along with a new shading category, and move smooth shading into it ([8e17737](https://github.com/hugemenace/nd/commit/8e17737030ec33248bfd2f1a2e126e76c68b2fa1))
* add clean_utils and apply_modifiers ops as shortcuts in main UI panel ([7aba702](https://github.com/hugemenace/nd/commit/7aba702b7b6acdc92e881738e2bb550309a508e7))
* add clear_materials operator ([02c580b](https://github.com/hugemenace/nd/commit/02c580be622acbf4e08690580e3b3b9a145b567a))
* add CTRL + click modifier removal behaviour to all applicable operators ([1fcb674](https://github.com/hugemenace/nd/commit/1fcb674a4bddfc0900af34673a698a6bf152632a))
* add experimental mode toggle to preferences ([4a5a4d1](https://github.com/hugemenace/nd/commit/4a5a4d1b3d97dfe4703b1adc3a3a3c2d7c44df92))
* add mirror operation to boolean object fast menu predictions ([7df0fea](https://github.com/hugemenace/nd/commit/7df0fea743c4ee074b4d4afb8983ddfc1e168ea4))
* add mouse-step values to lattice, screw, array_cubed, circular_array operators ([22e53de](https://github.com/hugemenace/nd/commit/22e53def7c332bd9aca44fb1e9cf4d9f210c3096))
* add Shift + Alt + E keybinding for the Packaging menu ([f92d434](https://github.com/hugemenace/nd/commit/f92d43433088d359b87394d421758c2fdf51dcd0))
* add smooth shading and weighted normal operators to the fast-predict menu ([28b359a](https://github.com/hugemenace/nd/commit/28b359ae277221018e49079ac62d73411adbe725))
* add the id_material operator ([20b77a0](https://github.com/hugemenace/nd/commit/20b77a02284c31f615660ebaca082fc89fda66a9))
* add undo/redo/W/C event passthrough as experimental feature for geo_lift, panel, and view_align operators ([778b064](https://github.com/hugemenace/nd/commit/778b064b547fc1742f36509b65b716c885326772))
* allow bevel segments to be set via mouse movement when mouse values are enabled ([c9713bd](https://github.com/hugemenace/nd/commit/c9713bdd96b8edc4cc013a3e84d34af7b39b2fc0))
* allow customisation of the overlay base color ([b6fb7df](https://github.com/hugemenace/nd/commit/b6fb7df0c31d90139325cedbbf3c312b3751ea41))
* allow ID Materials to be actioned in both object and edit mode (face select) ([021efe2](https://github.com/hugemenace/nd/commit/021efe21cccc5944c77821372e461c53523fbdad))
* allow smooth shading operator to be used on multiple objects simultaneously ([3d52fc9](https://github.com/hugemenace/nd/commit/3d52fc9bd88bef3e03dd3a21ff47239ecef2bdb2))
* create a dedicated ID materials menu under Packaging, and a new assign-existing ID material operator ([b383f14](https://github.com/hugemenace/nd/commit/b383f147c68dd9a1238b5f35956e1cffaf1f0bb2))
* remove edge weights and vertex groups when clearing edge_bevel, or vertex_bevel operations ([bfac62e](https://github.com/hugemenace/nd/commit/bfac62e8eff638eba6f9ed74ce3e9b5347df4a95))
* set keep_sharp for the weighted_normal operator by default ([3856be3](https://github.com/hugemenace/nd/commit/3856be3707735ef36bf1aa75fe48481dbf6855cc))
* split applicable util ops into dedicated scene and export menus ([6422a49](https://github.com/hugemenace/nd/commit/6422a49a183e2fdf74136d995228f2ed3116275a))
* update the ID Materials menu to show a static list of all available colours with previews ([bf9d5c1](https://github.com/hugemenace/nd/commit/bf9d5c1bd718e032676e7fe14657ad4e5ed14c86))


### Bug Fixes

* ensure mod order is rectified when using the edge_bevel operator ([ecd49d9](https://github.com/hugemenace/nd/commit/ecd49d90087292a59397a6e73a55c5845180a77c))
* ensure select objects are made single-user when executing the apply_modifiers operator ([a5955fb](https://github.com/hugemenace/nd/commit/a5955fb6591f31d5a4869e52adc9dc4d4b2d5f06))
* explicitly import bpy.utils.previews in icons/__init__.py ([03f9f2b](https://github.com/hugemenace/nd/commit/03f9f2bb5c4f927ee579980535f96703c9991487))
* fix array_cubed manual input override locking ([374c00b](https://github.com/hugemenace/nd/commit/374c00b2cbef2c8eb8245c987c49e649a0314bb8))
* set profile_extrude's calculate edges option to false by default ([d4c7537](https://github.com/hugemenace/nd/commit/d4c75371b132074d2e2e6ebe19f35cc40029963e))

## [1.33.0](https://github.com/hugemenace/nd/compare/v1.32.0...v1.33.0) (2022-08-06)


### Features

* add clear scale and shrink/fatten to sketch menu for object and edit mode respectively ([7be4562](https://github.com/hugemenace/nd/commit/7be45625f952b338421281cfaef8fddff913af70))
* add curve support to array_cubed operator ([c9b7c88](https://github.com/hugemenace/nd/commit/c9b7c881ef0e597aeb0361a4ba4a699922cb3417))
* add curve support to screw operator ([a74a5e6](https://github.com/hugemenace/nd/commit/a74a5e6cb066ce150f5f7b6d76e57c2545714337))
* add curve support to simple_deform operator ([bb0fa11](https://github.com/hugemenace/nd/commit/bb0fa1191ae7d1ede1b514a0426590d8d5acb7ea))
* add mirror curve option to fast predict menu ([6a37a8b](https://github.com/hugemenace/nd/commit/6a37a8ba189b3ad9d4e58b88cf23e114f1260b1d))
* add option to mirror curve(s) ([def7b2c](https://github.com/hugemenace/nd/commit/def7b2ccbded75ba7714bd96617c11e6fbe1c623))
* add screw, array_cubed, and simple_deform curve operators to fast predict menu ([0602f21](https://github.com/hugemenace/nd/commit/0602f21b6a175a5fd4fab58a4b7234833de1cd7a))
* add toggleable exclusive view (x-ray option) option to geo_lift, panel, and view_align operators ([9fc75c1](https://github.com/hugemenace/nd/commit/9fc75c1e2772c32622dbca5e85d7c82d08f760a2))
* split clear_view into overlay (all & custom) options ([785fd60](https://github.com/hugemenace/nd/commit/785fd60057c63d2a606ed64738c518124d0bba93))


### Bug Fixes

* ensure make edge/face operation is always available in edit mode fast menu ([cbeffac](https://github.com/hugemenace/nd/commit/cbeffacdd72311429a5772f60a2b532bf6f692ea))
* ensure weld modifier removal does not prevent standard bevels from being recalled, and avoid removing HN bevel welds during apply-modifier operations ([64c36bd](https://github.com/hugemenace/nd/commit/64c36bdf22583f115f96e48d0e6aaccd4d60b3f3))
* fix lattice target object parenting behaviour ([3d8a16e](https://github.com/hugemenace/nd/commit/3d8a16eb9baad028050338b56d53a150b24783ed))
* fix the "no predictions found" edge case in the Fast menu with only surfacing recallable operators ([b36a447](https://github.com/hugemenace/nd/commit/b36a44742b58fcb7020f7e648045d96e0e54c50b))
* set width lower limit to zero on WN bevel operator ([5a5dd78](https://github.com/hugemenace/nd/commit/5a5dd7883ca04e8302bd201a1abf108f21798fb2))

## [1.32.0](https://github.com/hugemenace/nd/compare/v1.31.0...v1.32.0) (2022-06-25)


### Features

* add an option to toggle the sidebar / N-panel ([0799e0b](https://github.com/hugemenace/nd/commit/0799e0b6608df8eeacd47beb325297b0e52a8821))
* add calculate edges option to profile_extrude operator ([8d6ead4](https://github.com/hugemenace/nd/commit/8d6ead4785b12cd528d7cbb19a1f2ee7d248d392))
* add extrusion mode option to solidify operator ([5011a6f](https://github.com/hugemenace/nd/commit/5011a6f682316603478cec461b1c80b6cf5d2bf5))
* add interpolation mode to lattice operator and default to linear ([9fdd252](https://github.com/hugemenace/nd/commit/9fdd2520420dafe24c598af08892590679a92b70))
* add offset option to profile_extrude operator ([e62687c](https://github.com/hugemenace/nd/commit/e62687c2d4e56c516f8974c38a95d73ccb82c178))
* add solidify option to fast menu for non-manifold meshes ([a14b819](https://github.com/hugemenace/nd/commit/a14b8194156b4b8475ad21d5106202a9b99f6fdd))
* add the ability to recall previous edge bevel weights ([e381ab3](https://github.com/hugemenace/nd/commit/e381ab3e3543e4f959ac5724a398e31cadcba784))
* add toggle wireframe and disable utility modifier options to cycle operator ([a3a0bbc](https://github.com/hugemenace/nd/commit/a3a0bbc80857cd45cdbf60d1978ad5b175640027))
* enhance profile extrusion and solidification predictions in the Fast menu ([539f413](https://github.com/hugemenace/nd/commit/539f4138aaa8ac44c56d20f656d955c7c94112d4))
* ensure mirror modifiers are placed before finishing bevels in the modifier stack ([5751adb](https://github.com/hugemenace/nd/commit/5751adb9f421959a6aaac2f99a2e54724768cef7))
* rectify the mod order for lattice, simple_deform, profile_extrude, screw, solidify, array_cubed, and circular_array operators ([2ccb087](https://github.com/hugemenace/nd/commit/2ccb0879217f8a13cabbca98c45a8a6676359b9e))
* remove all disabled (viewport hidden) boolean modifiers when using the clean_utils operator ([96a82ab](https://github.com/hugemenace/nd/commit/96a82abebb86c0c7b198ac62e3d330d975a4680c))


### Bug Fixes

* add missing fast menu no prediction results section count ([ac391ae](https://github.com/hugemenace/nd/commit/ac391ae821c4a6435847714547416a8d79d1a857))
* add missing new_modifier imports to recon_poly, screw_head, set_origin, and triangulate operators ([b832ca2](https://github.com/hugemenace/nd/commit/b832ca2a9aaa958ba085f95affca374a11df6964))
* ensure single_vertex object has rotation and scale applied after creation ([7ce7f30](https://github.com/hugemenace/nd/commit/7ce7f3012ba5af7a42b0622b7c5b22cf15435313))
* fix edge_bevel width shift/precision and value formatting ([78c1cac](https://github.com/hugemenace/nd/commit/78c1cac9e3bb4bfea2a7219f70ad18eca22273b8))
* fix error/crash in clean_utils utility & add logic for lattice modifiers ([14cf8a8](https://github.com/hugemenace/nd/commit/14cf8a8b971f1a09f28420c0a195a724ee39847b))
* fix mesh_f2 addon detection in the Fast Predict menu ([499d96a](https://github.com/hugemenace/nd/commit/499d96a710d9efda3818c8c6be573ce20259ed87))
* fix no predictions logic in the fast menu ([1819997](https://github.com/hugemenace/nd/commit/1819997a673cee43bd006b98491e18467e813f75))
* fix poll method target object type check in cycle operator ([a286253](https://github.com/hugemenace/nd/commit/a2862533c996214d99aeb73cd98c4d4a3a3488ea))
* handle object/modifier removal errors more gracefully in clean_utils operator ([6da00af](https://github.com/hugemenace/nd/commit/6da00af63304bd8342059029c3a35f741c1b5a3b))
* unify and lower the merge and bisect thresholds for the mirror operator ([843c126](https://github.com/hugemenace/nd/commit/843c126b2ea56f7a1d8a5265f837cdca856669f7))

## [1.31.0](https://github.com/hugemenace/nd/compare/v1.30.0...v1.31.0) (2022-06-12)


### Features

* add clean geometry logic to view align, and allow view align to be immediately invoked on applicable geometry with an alt mode ([db144a6](https://github.com/hugemenace/nd/commit/db144a6b2073e4fad0b61ff4507c0581b7be2972))
* add collapsible sections and common shortcuts to the N panel menu ([e57bc0d](https://github.com/hugemenace/nd/commit/e57bc0da79545af100c32844cac419cd6b20e0d2))
* add inscribed and circumscribed options to recon_poly operator ([fa724c4](https://github.com/hugemenace/nd/commit/fa724c4c195f2b941ca7a9b1fd6308c054076913))
* add the panel, geo_lift, and view_align operators to fast menu single object form predictions ([94ea2ca](https://github.com/hugemenace/nd/commit/94ea2ca99f5de9ee1ba339437ab89f81d254c6be))
* automatically collapse new modifiers added to objects ([752de82](https://github.com/hugemenace/nd/commit/752de827b7c71ab48ceb355bfc8df4ab878e2cbd))
* extend inscribed and circumscribed feature to recon_poly inner_radius option & fix recall/revert behaviour ([1611885](https://github.com/hugemenace/nd/commit/161188565b9cce2d40aba8454d1037bce0988a89))
* remove problematic bevels from all boolean reference objects ([6349c4d](https://github.com/hugemenace/nd/commit/6349c4d658798cbe8774d119d27f0b3dda0f291d))


### Bug Fixes

* ensure viewport camera is always set to orthographic when using view_align operator ([ee5c03d](https://github.com/hugemenace/nd/commit/ee5c03db49deede90d5740a609a7606ce7750b3e))
* fix array_cubed count reset behaviour while respecting the currently specified offset value ([a1d5ca5](https://github.com/hugemenace/nd/commit/a1d5ca5ec3c8f2faa05e7f7d7ab1d4df9aa799f9))
* fix direct object view_align operation when utilising edges or vertices ([c5059eb](https://github.com/hugemenace/nd/commit/c5059eb58a37860c95d2f419eec985911d4f1cde))
* fix mirror across geometry behaviour and unneeded show_in_front assignment for evaluated geometry ([bd0f14f](https://github.com/hugemenace/nd/commit/bd0f14f39d59ffc8656d8ceaa9a8fc423f715262))
* fix up single and multi-object geometry mirror object evaluation and empty parenting ([e7220ad](https://github.com/hugemenace/nd/commit/e7220adbe7b6ba3d11a4a6677fe8c600bbc8a462))

## [1.30.0](https://github.com/hugemenace/nd/compare/v1.29.0...v1.30.0) (2022-06-06)


### Features

* add additional screw head types (@Shaddow) ([b130d78](https://github.com/hugemenace/nd/commit/b130d78873608180d719fc9e4bad4146a00c27f3))
* add better boolean and sketch detection in the fast prediction menu ([3c06550](https://github.com/hugemenace/nd/commit/3c065502b3e13cfd019337b0cb7c9bf10ea5879f))
* add clean_utils operator ([3f4e47b](https://github.com/hugemenace/nd/commit/3f4e47bfd8f335afb21c05fa82cc8a788c907e9f))
* perform additional geometry cleanup when extracting faces using the panel operator ([9e53d4b](https://github.com/hugemenace/nd/commit/9e53d4b2e644f1e4bc66a687161b5f05a0fb8274))


### Bug Fixes

* ensure boolean swap_solver updates only apply to objects referencing the selected utils ([6845d30](https://github.com/hugemenace/nd/commit/6845d300bf0b3cf22909848edf5b6e015b03c5c1))
* ensure clean_utils also handles mirror and array empty objects in utils collection ([43c0c82](https://github.com/hugemenace/nd/commit/43c0c822f964be175a5b38461bf3a1da8267a6dc))
* ensure that individual faces cannot be toggled until the inset stage in the panel operator ([e6cb10f](https://github.com/hugemenace/nd/commit/e6cb10f4914e7958a132c3263b0371d19a623423))
* fix create_duplicate_liftable_geometry object_name parameter being overridden ([11d7b4b](https://github.com/hugemenace/nd/commit/11d7b4b76f43d33c4034b0803d431d1be5f809f8))
* fix error when using swap solver on a utility referenced by an object with invalid boolean modifiers present ([20045ed](https://github.com/hugemenace/nd/commit/20045ed2ef6f7bcc70263e216935dde89355f741))
* fix NoneType object error when cycling through a utility object ([4a5a402](https://github.com/hugemenace/nd/commit/4a5a402a35e9f468db9f9043d0b81fe805225199))

## [1.29.0](https://github.com/hugemenace/nd/compare/v1.28.4...v1.29.0) (2022-06-02)


### Features

* add hard-apply mode to apply_modifiers utility, and exclude regular multi segment edge bevels from normal usage ([a5ee288](https://github.com/hugemenace/nd/commit/a5ee2886f588f9f820f9b808edbffae2e4e5ba53))
* add mirror operator to the fast menu for profile predictions ([74f2545](https://github.com/hugemenace/nd/commit/74f25458a7c2216f4382253a5a9152f4ab1c4879))
* add ND theme (color) options to preferences ([1d25644](https://github.com/hugemenace/nd/commit/1d2564421f805c181b8d2af9fbc7da5e29586223))
* add panel operator ([a4e76aa](https://github.com/hugemenace/nd/commit/a4e76aab511733ae6837fedfd7e99e76ca97951e))
* add recon poly detection to fast menu ([de87d9b](https://github.com/hugemenace/nd/commit/de87d9b50fd45a28a758ab3d1c27fdf6b345aebc))
* add remaining boolean operations to the fast menu ([5db12e6](https://github.com/hugemenace/nd/commit/5db12e6a8473b08cbb705416f5aeac1a77db16c5))
* add shift alt-mode to set_origin utility to undo faux origin translations ([43202bf](https://github.com/hugemenace/nd/commit/43202bfe57d5c7dd4900c0ff4b71839b4a0a33f3))
* add solidify and profile extrude options to the fast menu when operators have been previously performed on the selected object ([84fa5a0](https://github.com/hugemenace/nd/commit/84fa5a0855dc64dee6f1ea3c20a427a395bd0609))
* clean up duplicated mesh by default when using geo_lift or panel operators, with option to preserve geometry ([d27a8ab](https://github.com/hugemenace/nd/commit/d27a8aba71b7e43b043d4bf9b73faa7f2f3e7187))
* detect additional existing mods in fast menu ([c0a5963](https://github.com/hugemenace/nd/commit/c0a5963f0ac8b263265f0aaf296e23e5f095ec56))
* ensure starting geometry is reselected when reverting geo_lift operator ([321d2c9](https://github.com/hugemenace/nd/commit/321d2c91af8c49af39938373bf98aadca4e3325f))
* harden up circular_array operator, add displacement axis option, and regular/faux origin alt mode ([48b5040](https://github.com/hugemenace/nd/commit/48b5040db100ce3fcc73859f48cb6fb050cc7254))


### Bug Fixes

* add an additional clause to the circular_array poll method ([11dc8ee](https://github.com/hugemenace/nd/commit/11dc8eeca5a00fd135274ab7063f35cd3511df06))
* add missing continue statements in create_duplicate_liftable_geometry ([c6c9aad](https://github.com/hugemenace/nd/commit/c6c9aad3f89998310d49cd158ca75183e63632f7))
* ensure the inset stage only begins if one or more faces have been selected when using the panel operator ([fd26650](https://github.com/hugemenace/nd/commit/fd26650439d101d7605e09e81b53b393ad2b5a6b))
* ensure the reference object origin is restored when cancelling a new circular array operation ([00be593](https://github.com/hugemenace/nd/commit/00be593adf63ffde82ebef0ceeabd9b7dd0b759e))
* fix mod reference error in create_duplicate_liftable_geometry function in object library ([979646d](https://github.com/hugemenace/nd/commit/979646dceb470d2e33975a7569a87c0934156408))
* fix profile extrude recall and revert behaviour ([a9a870d](https://github.com/hugemenace/nd/commit/a9a870d599a7581b56251c6cf5fc83e2d62778b8))
* fix recon poly local Z axis natural rotation and recall ability ([85e91a1](https://github.com/hugemenace/nd/commit/85e91a17e925d79db95b5f8427aad7dd20e8fefe))
* tidy up and fix undesired relative offset behaviour in panel operator ([91bbb06](https://github.com/hugemenace/nd/commit/91bbb060d4235b8c3f7e3bd67411d6c7ea358080))

### [1.28.4](https://github.com/hugemenace/nd/compare/v1.28.3...v1.28.4) (2022-05-28)


### Bug Fixes

* add additional checks to bevel types in automatic modifier reordering logic ([73ce5cf](https://github.com/hugemenace/nd/commit/73ce5cf8926a0e2685708e183e63b191542c6abc))

### [1.28.3](https://github.com/hugemenace/nd/compare/v1.28.2...v1.28.3) (2022-05-28)


### Bug Fixes

* fix modifier stack ordering when vertex bevel + weld modifiers are present ([4b6a4da](https://github.com/hugemenace/nd/commit/4b6a4da5cbbbc4aa68aa751eaceee3b134cf4ab1))

### [1.28.2](https://github.com/hugemenace/nd/compare/v1.28.1...v1.28.2) (2022-05-27)

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
