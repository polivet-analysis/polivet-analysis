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
