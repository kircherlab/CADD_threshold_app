# Changelog

## [0.0.10](https://github.com/kircherlab/CADD_threshold_app/compare/v0.0.9...v0.0.10) (2026-08-26)


### Bug Fixes

* correctly run pandas when parsing gene list ([#33](https://github.com/kircherlab/CADD_threshold_app/issues/33)) ([980a24c](https://github.com/kircherlab/CADD_threshold_app/commit/980a24c5653d859454aea8e25e8fd82a5b05b5d8))
* file upload for genes excepts other seperators ([#31](https://github.com/kircherlab/CADD_threshold_app/issues/31)) ([d47514c](https://github.com/kircherlab/CADD_threshold_app/commit/d47514c54090d26c49d23fff98c5e4346ea67758))

## [0.0.9](https://github.com/kircherlab/CADD_threshold_app/compare/v0.0.8...v0.0.9) (2026-07-29)


### Features

* new layout ([#25](https://github.com/kircherlab/CADD_threshold_app/issues/25)) ([b1e27a9](https://github.com/kircherlab/CADD_threshold_app/commit/b1e27a9456086efcc712a5a9e7da86e2f9b1f8dd))

## [0.0.8](https://github.com/kircherlab/CADD_threshold_app/compare/v0.0.7...v0.0.8) (2026-07-27)


### Features

* 📈 Support indicator for gene panles and specific gene lists  ([#23](https://github.com/kircherlab/CADD_threshold_app/issues/23)) ([c366e28](https://github.com/kircherlab/CADD_threshold_app/commit/c366e28850f8e35c07804a0b01e6cd9c97178fe5))

## [0.0.7](https://github.com/kircherlab/CADD_threshold_app/compare/v0.0.6...v0.0.7) (2026-06-19)


### Bug Fixes

* no k with numbers in line graphs ([#21](https://github.com/kircherlab/CADD_threshold_app/issues/21)) ([c786628](https://github.com/kircherlab/CADD_threshold_app/commit/c7866286d535e0c5171f96cc28439a032669e6b1))


### Documentation

* https://cadd-threshold.kircherlab.bihealth.org in readme ([1b42298](https://github.com/kircherlab/CADD_threshold_app/commit/1b422984c87cd4b73cf0d5561451a43383d71d89))

## [0.0.6](https://github.com/kircherlab/CADD_threshold_app/compare/v0.0.5...v0.0.6) (2026-05-27)


### Features

* basic_plot has now two y-axis, Genes and Panel are shown in Line Plot, Disclaimer for calculating many genes ([c1434ae](https://github.com/kircherlab/CADD_threshold_app/commit/c1434ae3f84220f66e3b4a4f116c4ce18036faa5))
* tp, tn, fp, fn can be viewed as percentages in the basic_plots ([8940219](https://github.com/kircherlab/CADD_threshold_app/commit/89402197d5d4a16f37e8ec66cf34c0f6e7941f3b))


### Bug Fixes

* changed "Specifity" in data header to "Specificity" ([2998a13](https://github.com/kircherlab/CADD_threshold_app/commit/2998a13e91695de3ee1901b8dab6a695e695259e))
* startup issue loading data before environment path ([01bcad2](https://github.com/kircherlab/CADD_threshold_app/commit/01bcad2cc4864b3c90a1979e05945467a7181d3f))
* too complex function ([f8e1e86](https://github.com/kircherlab/CADD_threshold_app/commit/f8e1e86dae6cd8b8fcb0b6e5359eb01ad1f6c937))
* trying to fix linting error ([59a842d](https://github.com/kircherlab/CADD_threshold_app/commit/59a842d259c4b49f8e98d1017db39a874cb3b455))


### Documentation

* changed the "about dataset" description so it can be edited dynamically with the data files ([712aca8](https://github.com/kircherlab/CADD_threshold_app/commit/712aca82becc52b17df9006dfe137e10b35c216c))
* documented the changes in README ([73576db](https://github.com/kircherlab/CADD_threshold_app/commit/73576db9e7aabe10b35a89fbabccb91cb329d2bb))
* Improve data download instructions in README ([88ade0b](https://github.com/kircherlab/CADD_threshold_app/commit/88ade0b731441ef3785477b2c2987ce577fe1a15))
* updated README ([33abdeb](https://github.com/kircherlab/CADD_threshold_app/commit/33abdeb8287202947555d3b15bc9590019295c29))

## [0.0.5](https://github.com/kircherlab/CADD_threshold_app/compare/v0.0.4...v0.0.5) (2026-04-14)


### Bug Fixes

* **app:** :rotating_light: Use /www static mount and update asset paths for Starlette compatibility ([ecaeb63](https://github.com/kircherlab/CADD_threshold_app/commit/ecaeb6391e59cd7e2a7f982913661e062023d1f6))
* **app:** add websocket route alias ([faa96e0](https://github.com/kircherlab/CADD_threshold_app/commit/faa96e0a7523e2dc0ca5708ecae1adba83a25d93))

## [0.0.4](https://github.com/kircherlab/CADD_threshold_app/compare/v0.0.3...v0.0.4) (2026-04-13)


### Bug Fixes

* :ambulance: adding favicon ([#11](https://github.com/kircherlab/CADD_threshold_app/issues/11)) ([f680be7](https://github.com/kircherlab/CADD_threshold_app/commit/f680be72f6bd4e4855e91325f4b969088a246e66))

## [0.0.3](https://github.com/kircherlab/CADD_threshold_app/compare/v0.0.2...v0.0.3) (2026-04-02)


### Bug Fixes

* OSError when loading not available panel data ([#8](https://github.com/kircherlab/CADD_threshold_app/issues/8)) ([11bf907](https://github.com/kircherlab/CADD_threshold_app/commit/11bf907c716f3ef5dce54f205bccc2db440ac19c))

## [0.0.2](https://github.com/kircherlab/CADD_threshold_app/compare/v0.0.1...v0.0.2) (2026-04-01)


### Bug Fixes

* Fixing panel an gene set data loading ([#6](https://github.com/kircherlab/CADD_threshold_app/issues/6)) ([0234e3a](https://github.com/kircherlab/CADD_threshold_app/commit/0234e3aba3a80b6fd45f5819095eebe2925a4777))

## [0.0.1](https://github.com/kircherlab/CADD_threshold_app/compare/v0.0.0...v0.0.1) (2026-03-24)


### Features

* update dependencies and refactor main function to use Click for command-line options ([0bc626e](https://github.com/kircherlab/CADD_threshold_app/commit/0bc626e56fe4888533b71b492ae7a61376f002bb))

## 0.0.0 (2026-03-03)


Initial release!
