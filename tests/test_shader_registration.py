from pycreative import graphics


def test_pcshader_registration_and_default_vertex():
    s = graphics.PCShader(frag_source="void main() { gl_FragColor = vec4(1.0); }")
    # The shader should be registered in the module registry
    assert s in graphics._REGISTERED_SHADERS
    # Since no vertex shader was provided, a default should have been assigned
    assert s.vert_source is not None
    assert isinstance(s.vert_source, str)
