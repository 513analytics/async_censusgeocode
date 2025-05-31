# -*- coding: utf-8 -*-

# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copyright (c) 2025, Bryan Corder <contact@fakeisthenewreal.org>

from .async_censusgeocode import AsyncCensusGeocode

acg = AsyncCensusGeocode()

coordinates = acg.coordinates
address = acg.address
onelineaddress = acg.onelineaddress
addressbatch = acg.addressbatch
