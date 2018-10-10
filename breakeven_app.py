''' Present an interactive function explorer with slider widgets.
Scrub the sliders to change the properties of the ``sin`` curve, or
type into the title text box to update the title of the plot.
Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve sliders.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/sliders
in your browser.
'''
import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, layout, column
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import Slider, TextInput
from bokeh.plotting import figure,output_file,show

# Set up data


MAX_CAPACITY_UTILIZATION = .9
CONST_REVENUE_PER_KG_CURRENT_AVG = 1.9 #August rev per kg
CONST_COST_PER_KG_CURRENT_AVG = 3.9 # august cost per kg
CONST_LH_COST_PER_KM_excl_helper_incl_incentive = 10
CONST_MR_COST_PER_DAY_PER_TRANSPORTER_excl_helper_incl_incentive = 1000
CONST_MR_WEIGHT_CEILING_PER_DAY_PER_TRANSPORTER_KG = 1500 # according to sharath
current_avg_MR_weight_per_day_per_transporter_hubli_KG = 450 # based on data
current_avg_mr_productivity = current_avg_MR_weight_per_day_per_transporter_hubli_KG/CONST_MR_WEIGHT_CEILING_PER_DAY_PER_TRANSPORTER_KG
CONST_CARRYING_CAPACITY_PER_TRUCK_KG = 750
current_net_utilization_average = .25
CONST_AVG_LH_DIST_HUB_TO_HUB_TO_AND_FRO_KM = 70
CONST_TOTAL_DIST_PER_ORDER_KM = 90
helper_cost_per_day = 300
CONST_MR_NUM_TASKS_PER_DAY_PER_TRANSPORTER_CEILING = 35
current_average_mr_km_per_day = 37
current_average_mr_num_tasks_per_day_per_transporter = 12
SOURCE_MR_KM_PER_ORDER = current_average_mr_km_per_day / current_average_mr_num_tasks_per_day_per_transporter


DEST_MR_KM_PER_ORDER = CONST_TOTAL_DIST_PER_ORDER_KM - CONST_AVG_LH_DIST_HUB_TO_HUB_TO_AND_FRO_KM - SOURCE_MR_KM_PER_ORDER
LH_COST_PER_LOAD = CONST_LH_COST_PER_KM_excl_helper_incl_incentive * (CONST_AVG_LH_DIST_HUB_TO_HUB_TO_AND_FRO_KM+DEST_MR_KM_PER_ORDER)

lh_cost_per_kg_ideal = LH_COST_PER_LOAD / (CONST_CARRYING_CAPACITY_PER_TRUCK_KG* MAX_CAPACITY_UTILIZATION)
mr_cost_per_kg_ideal = CONST_MR_COST_PER_DAY_PER_TRANSPORTER_excl_helper_incl_incentive / (CONST_MR_WEIGHT_CEILING_PER_DAY_PER_TRANSPORTER_KG*MAX_CAPACITY_UTILIZATION)
helper_cost_per_kg_ideal = helper_cost_per_day / (CONST_MR_WEIGHT_CEILING_PER_DAY_PER_TRANSPORTER_KG * MAX_CAPACITY_UTILIZATION)

lh_cost_per_kg_current = LH_COST_PER_LOAD / (CONST_CARRYING_CAPACITY_PER_TRUCK_KG * current_net_utilization_average)
mr_cost_per_kg_current = (CONST_MR_COST_PER_DAY_PER_TRANSPORTER_excl_helper_incl_incentive / 
                          (CONST_MR_WEIGHT_CEILING_PER_DAY_PER_TRANSPORTER_KG*current_avg_mr_productivity))
helper_cost_per_kg_current = helper_cost_per_day / (CONST_MR_WEIGHT_CEILING_PER_DAY_PER_TRANSPORTER_KG * current_avg_mr_productivity)


#calculate ideal and current cost per kg and scale them using cost per kg from data
cost_per_kg_ideal = lh_cost_per_kg_ideal+mr_cost_per_kg_ideal+helper_cost_per_kg_ideal
cost_per_kg_current = lh_cost_per_kg_current+mr_cost_per_kg_current+helper_cost_per_kg_current

div_factor = cost_per_kg_current / CONST_COST_PER_KG_CURRENT_AVG

lh_utils = [.25,.30,.35,.40,.45,.50,.55,.60,.65,.70,.75,.80,.85,.90]

mr_util = .30
cost_per_kg = []
for i in lh_utils:

    lh_cost_per_kg_iter = LH_COST_PER_LOAD / (CONST_CARRYING_CAPACITY_PER_TRUCK_KG * i)
    mr_cost_per_kg_iter = (CONST_MR_COST_PER_DAY_PER_TRANSPORTER_excl_helper_incl_incentive / 
                          (CONST_MR_WEIGHT_CEILING_PER_DAY_PER_TRANSPORTER_KG*mr_util))
    helper_cost_per_kg_iter = helper_cost_per_day / (CONST_MR_WEIGHT_CEILING_PER_DAY_PER_TRANSPORTER_KG * mr_util)
    
    cost_per_kg_iter = lh_cost_per_kg_iter+mr_cost_per_kg_iter+helper_cost_per_kg_iter
    cost_per_kg.append(cost_per_kg_iter/div_factor)

source = ColumnDataSource(data=dict(x=lh_utils, y=cost_per_kg))

# Set up plot
plot = figure(plot_height=600, plot_width=700, title="Cost Per Kg Vs LH Utilisation",
            tools="crosshair,pan,reset,save,wheel_zoom,hover",
              x_range=[.25,1], y_range=[1,5])

hover = plot.select(dict(type=HoverTool))

hover.tooltips = [("LH Utilisation","$x"),("Cost Per KG","$y")]
plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)



# Set up widgets
mr_util_slider = Slider(title="MR Productivity", value=mr_util, start=mr_util, end=1.0, step=0.05)
helper_cost_slider = Slider(title="% Helper Cost Externalised", value=0, start=0, end=1, step=0.1)


def update_data(attrname, old, new):

    # Get the current slider values
    mr_util = mr_util_slider.value
    helper_cost_externalized = helper_cost_slider.value

    cost_per_kg = []
    for i in lh_utils:

        lh_cost_per_kg_iter = LH_COST_PER_LOAD / (CONST_CARRYING_CAPACITY_PER_TRUCK_KG * i)
        mr_cost_per_kg_iter = (CONST_MR_COST_PER_DAY_PER_TRANSPORTER_excl_helper_incl_incentive / 
                          (CONST_MR_WEIGHT_CEILING_PER_DAY_PER_TRANSPORTER_KG*mr_util))
        helper_cost_per_kg_iter = (helper_cost_per_day*(1-helper_cost_externalized)) / (CONST_MR_WEIGHT_CEILING_PER_DAY_PER_TRANSPORTER_KG * mr_util)
    
        cost_per_kg_iter = lh_cost_per_kg_iter+mr_cost_per_kg_iter+helper_cost_per_kg_iter
    
        cost_per_kg.append(cost_per_kg_iter/div_factor)

    source.data = dict(x=lh_utils, y=cost_per_kg)

for w in [mr_util_slider,helper_cost_slider]:
    w.on_change('value', update_data)



# Set up layouts and add to document
inputs = widgetbox(mr_util_slider,helper_cost_slider)
#widgets = widgetbox(mr_util_slider,helper_cost_slider)
#plt = row(plot,)
#l = column(widgets,plot)
curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "Break Even Scenarios"

