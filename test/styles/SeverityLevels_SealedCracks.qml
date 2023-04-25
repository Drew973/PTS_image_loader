<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingTol="1" styleCategories="AllStyleCategories" version="3.10.4-A Coruña" minScale="1e+08" simplifyMaxScale="1" simplifyDrawingHints="1" readOnly="0" maxScale="0" hasScaleBasedVisibilityFlag="0" simplifyLocal="1" labelsEnabled="0" simplifyAlgorithm="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 enableorderby="0" forceraster="0" symbollevels="0" type="singleSymbol">
    <symbols>
      <symbol force_rhr="0" clip_to_extent="1" alpha="1" name="0" type="line">
        <layer locked="0" class="SimpleLine" enabled="1" pass="0">
          <prop k="capstyle" v="square"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="draw_inside_polygon" v="0"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="line_color" v="251,22,225,255"/>
          <prop k="line_style" v="dash"/>
          <prop k="line_width" v="0.26"/>
          <prop k="line_width_unit" v="MM"/>
          <prop k="offset" v="0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="ring_filter" v="0"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
  </renderer-v2>
  <customproperties>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="variableNames"/>
    <property key="variableValues"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <SingleCategoryDiagramRenderer attributeLegend="1" diagramType="Histogram">
    <DiagramCategory enabled="0" lineSizeType="MM" sizeType="MM" width="15" height="15" diagramOrientation="Up" opacity="1" backgroundAlpha="255" backgroundColor="#ffffff" minScaleDenominator="0" barWidth="5" sizeScale="3x:0,0,0,0,0,0" maxScaleDenominator="1e+08" scaleDependency="Area" penWidth="0" penAlpha="255" lineSizeScale="3x:0,0,0,0,0,0" rotationOffset="270" minimumSize="0" labelPlacementMethod="XHeight" penColor="#000000" scaleBasedVisibility="0">
      <fontProperties description="MS Shell Dlg 2,9.75,-1,5,50,0,0,0,0,0" style=""/>
    </DiagramCategory>
  </SingleCategoryDiagramRenderer>
  <DiagramLayerSettings showAll="1" dist="0" priority="0" obstacle="0" linePlacementFlags="18" zIndex="0" placement="2">
    <properties>
      <Option type="Map">
        <Option name="name" type="QString" value=""/>
        <Option name="properties"/>
        <Option name="type" type="QString" value="collection"/>
      </Option>
    </properties>
  </DiagramLayerSettings>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks/>
    <checkConfiguration/>
  </geometryOptions>
  <fieldConfiguration>
    <field name="fileName">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="sectionID">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="sealedCrackID">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="nodeID">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="xValue">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="yValue">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias field="fileName" index="0" name=""/>
    <alias field="sectionID" index="1" name=""/>
    <alias field="sealedCrackID" index="2" name=""/>
    <alias field="nodeID" index="3" name=""/>
    <alias field="xValue" index="4" name=""/>
    <alias field="yValue" index="5" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default field="fileName" expression="" applyOnUpdate="0"/>
    <default field="sectionID" expression="" applyOnUpdate="0"/>
    <default field="sealedCrackID" expression="" applyOnUpdate="0"/>
    <default field="nodeID" expression="" applyOnUpdate="0"/>
    <default field="xValue" expression="" applyOnUpdate="0"/>
    <default field="yValue" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint field="fileName" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="sectionID" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="sealedCrackID" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="nodeID" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="xValue" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="yValue" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="fileName" desc=""/>
    <constraint exp="" field="sectionID" desc=""/>
    <constraint exp="" field="sealedCrackID" desc=""/>
    <constraint exp="" field="nodeID" desc=""/>
    <constraint exp="" field="xValue" desc=""/>
    <constraint exp="" field="yValue" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column hidden="0" name="fileName" width="-1" type="field"/>
      <column hidden="0" name="sectionID" width="-1" type="field"/>
      <column hidden="0" name="sealedCrackID" width="-1" type="field"/>
      <column hidden="0" name="nodeID" width="-1" type="field"/>
      <column hidden="0" name="xValue" width="-1" type="field"/>
      <column hidden="0" name="yValue" width="-1" type="field"/>
      <column hidden="1" width="-1" type="actions"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
	geom = feature.geometry()
	control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="fileName" editable="1"/>
    <field name="nodeID" editable="1"/>
    <field name="sealedCrackID" editable="1"/>
    <field name="sectionID" editable="1"/>
    <field name="xValue" editable="1"/>
    <field name="yValue" editable="1"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="fileName"/>
    <field labelOnTop="0" name="nodeID"/>
    <field labelOnTop="0" name="sealedCrackID"/>
    <field labelOnTop="0" name="sectionID"/>
    <field labelOnTop="0" name="xValue"/>
    <field labelOnTop="0" name="yValue"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>fileName</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>1</layerGeometryType>
</qgis>
