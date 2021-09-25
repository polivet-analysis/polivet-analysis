#
#     Copyright (C) 2021  Tatiana Novosadjuk & Victoria Tsvetkova
#
#     This file is part of Polevet-SPb-2020.
#
#     Polevet-SPb-2020 is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Polevet-SPb-2020 is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Polevet-SPb-2020.  If not, see <https://www.gnu.org/licenses/>.
#

from core.analytics import Analytics

analytics = Analytics('temp/data.h5', particle_id=0)

for i in range(20):
    print(str(i))
    analytics.get_all_trajectories_fig()

    print("2")
    analytics.get_trajectory_stat_fig()

    print("3")
    analytics.get_msd_for_particles_fig()

    print("4")
    analytics.get_x_displacement_fig()

    print("5")
    analytics.get_y_displacement_fig()

print("Finish")
input()
