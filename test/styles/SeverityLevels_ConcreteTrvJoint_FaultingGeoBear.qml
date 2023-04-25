<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.16.0-Hannover" styleCategories="Symbology">
  <renderer-v2 type="RuleRenderer" enableorderby="0" forceraster="0" symbollevels="0">
    <rules key="{840d9318-cd82-401f-acb9-3f5f55247841}">
      <rule symbol="0" filter="&quot;faulting&quot; &lt;= 0 OR &quot;faulting&quot; >=0" key="{0edc07f5-46c2-48d4-976e-9208e198c9e7}" label="Severity 1"/>
      <rule symbol="1" filter="&quot;faulting&quot; &lt; -5 OR &quot;faulting&quot; > 5" key="{adeb3a72-86a6-43e7-a064-2a254ee2a557}" label="Severity 2"/>
      <rule symbol="2" filter="&quot;faulting&quot; &lt; -10 OR &quot;faulting&quot; > 10" key="{52fc0b85-9788-4078-ac4b-c67f130414c4}" label="Severity 3"/>
    </rules>
    <symbols>
      <symbol alpha="1" type="fill" clip_to_extent="1" force_rhr="0" name="0">
        <layer pass="0" enabled="1" locked="0" class="SimpleFill">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="1,255,35,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="35,35,35,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" type="fill" clip_to_extent="1" force_rhr="0" name="1">
        <layer pass="0" enabled="1" locked="0" class="SimpleFill">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="255,147,5,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="21,21,21,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
      <symbol alpha="1" type="fill" clip_to_extent="1" force_rhr="0" name="2">
        <layer pass="0" enabled="1" locked="0" class="SimpleFill">
          <prop v="3x:0,0,0,0,0,0" k="border_width_map_unit_scale"/>
          <prop v="255,1,26,255" k="color"/>
          <prop v="bevel" k="joinstyle"/>
          <prop v="0,0" k="offset"/>
          <prop v="3x:0,0,0,0,0,0" k="offset_map_unit_scale"/>
          <prop v="MM" k="offset_unit"/>
          <prop v="21,21,21,255" k="outline_color"/>
          <prop v="solid" k="outline_style"/>
          <prop v="0.26" k="outline_width"/>
          <prop v="MM" k="outline_width_unit"/>
          <prop v="solid" k="style"/>
          <data_defined_properties>
            <Option type="Map">
              <Option type="QString" name="name" value=""/>
              <Option name="properties"/>
              <Option type="QString" name="type" value="collection"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerGeometryType>2</layerGeometryType>
</qgis>
