<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis simplifyDrawingTol="1" styleCategories="AllStyleCategories" version="3.10.4-A Coruña" minScale="1e+08" simplifyMaxScale="1" simplifyDrawingHints="1" readOnly="0" maxScale="0" hasScaleBasedVisibilityFlag="0" simplifyLocal="1" labelsEnabled="0" simplifyAlgorithm="0">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <renderer-v2 enableorderby="0" forceraster="0" symbollevels="0" type="RuleRenderer">
    <rules key="{f6cb8d99-e4c3-4967-8944-3a2655aa9058}">
      <rule key="{6b105d8e-a44f-4c31-9682-39405884be70}" symbol="0" filter=" depth >'6' AND depth &lt;= '13'" label="Severity 1"/>
      <rule key="{c5d425c3-026f-4c33-8579-aff5efb4311e}" symbol="1" filter="depth >= '13' AND depth &lt; '25'" label="Severity 2"/>
      <rule key="{ddbbf4d6-6c02-443a-badb-23ed629e27ba}" symbol="2" filter="depth > '25'" label="Severity 3"/>
    </rules>
    <symbols>
      <symbol force_rhr="0" clip_to_extent="1" alpha="0.25" name="0" type="fill">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="1,255,35,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" clip_to_extent="1" alpha="0.25" name="1" type="fill">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="255,147,5,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
          <data_defined_properties>
            <Option type="Map">
              <Option name="name" type="QString" value=""/>
              <Option name="properties"/>
              <Option name="type" type="QString" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol force_rhr="0" clip_to_extent="1" alpha="0.25" name="2" type="fill">
        <layer locked="0" class="SimpleFill" enabled="1" pass="0">
          <prop k="border_width_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="color" v="255,9,1,255"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0,0"/>
          <prop k="offset_map_unit_scale" v="3x:0,0,0,0,0,0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="outline_color" v="35,35,35,255"/>
          <prop k="outline_style" v="solid"/>
          <prop k="outline_width" v="0.26"/>
          <prop k="outline_width_unit" v="MM"/>
          <prop k="style" v="solid"/>
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
  <DiagramLayerSettings showAll="1" dist="0" priority="0" obstacle="0" linePlacementFlags="18" zIndex="0" placement="1">
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
    <checkConfiguration type="Map">
      <Option name="QgsGeometryGapCheck" type="Map">
        <Option name="allowedGapsBuffer" type="double" value="0"/>
        <Option name="allowedGapsEnabled" type="bool" value="false"/>
        <Option name="allowedGapsLayer" type="QString" value=""/>
      </Option>
    </checkConfiguration>
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
    <field name="station">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="wheeltrack">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="depth">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="width">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="crossSection">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="type">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field name="percentageDeformation">
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
    <alias field="station" index="2" name=""/>
    <alias field="wheeltrack" index="3" name=""/>
    <alias field="depth" index="4" name=""/>
    <alias field="width" index="5" name=""/>
    <alias field="crossSection" index="6" name=""/>
    <alias field="type" index="7" name=""/>
    <alias field="percentageDeformation" index="8" name=""/>
  </aliases>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <defaults>
    <default field="fileName" expression="" applyOnUpdate="0"/>
    <default field="sectionID" expression="" applyOnUpdate="0"/>
    <default field="station" expression="" applyOnUpdate="0"/>
    <default field="wheeltrack" expression="" applyOnUpdate="0"/>
    <default field="depth" expression="" applyOnUpdate="0"/>
    <default field="width" expression="" applyOnUpdate="0"/>
    <default field="crossSection" expression="" applyOnUpdate="0"/>
    <default field="type" expression="" applyOnUpdate="0"/>
    <default field="percentageDeformation" expression="" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint field="fileName" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="sectionID" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="station" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="wheeltrack" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="depth" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="width" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="crossSection" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="type" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
    <constraint field="percentageDeformation" notnull_strength="0" exp_strength="0" unique_strength="0" constraints="0"/>
  </constraints>
  <constraintExpressions>
    <constraint exp="" field="fileName" desc=""/>
    <constraint exp="" field="sectionID" desc=""/>
    <constraint exp="" field="station" desc=""/>
    <constraint exp="" field="wheeltrack" desc=""/>
    <constraint exp="" field="depth" desc=""/>
    <constraint exp="" field="width" desc=""/>
    <constraint exp="" field="crossSection" desc=""/>
    <constraint exp="" field="type" desc=""/>
    <constraint exp="" field="percentageDeformation" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig actionWidgetStyle="dropDown" sortExpression="" sortOrder="0">
    <columns>
      <column hidden="0" name="fileName" width="-1" type="field"/>
      <column hidden="0" name="sectionID" width="-1" type="field"/>
      <column hidden="0" name="station" width="-1" type="field"/>
      <column hidden="0" name="wheeltrack" width="-1" type="field"/>
      <column hidden="0" name="depth" width="-1" type="field"/>
      <column hidden="0" name="width" width="-1" type="field"/>
      <column hidden="0" name="crossSection" width="-1" type="field"/>
      <column hidden="0" name="type" width="-1" type="field"/>
      <column hidden="0" name="percentageDeformation" width="-1" type="field"/>
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
    <field name="crossSection" editable="1"/>
    <field name="depth" editable="1"/>
    <field name="fileName" editable="1"/>
    <field name="percentageDeformation" editable="1"/>
    <field name="sectionID" editable="1"/>
    <field name="station" editable="1"/>
    <field name="type" editable="1"/>
    <field name="wheeltrack" editable="1"/>
    <field name="width" editable="1"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="crossSection"/>
    <field labelOnTop="0" name="depth"/>
    <field labelOnTop="0" name="fileName"/>
    <field labelOnTop="0" name="percentageDeformation"/>
    <field labelOnTop="0" name="sectionID"/>
    <field labelOnTop="0" name="station"/>
    <field labelOnTop="0" name="type"/>
    <field labelOnTop="0" name="wheeltrack"/>
    <field labelOnTop="0" name="width"/>
  </labelOnTop>
  <widgets/>
  <previewExpression>fileName</previewExpression>
  <mapTip></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
