uniform float time;
uniform int levels;
varying vec3 N;
varying vec3 v;


float quantize(float _intensity, int _levels)
{
    return int(_intensity*_levels)/float(_levels);
}

void main()
{
    
    vec3 L = normalize(gl_LightSource[0].position.xyz - v);   
    vec3 E = normalize(-v); // we are in Eye Coordinates, so EyePos is (0,0,0)  
    vec3 R = normalize(-reflect(L,N));  
    float intensity = dot(L,N);
 
    vec4 Iamb = gl_FrontLightProduct[0].ambient;    

    vec4 Idiff = gl_FrontLightProduct[0].diffuse * max(dot(N,L), 0.0);
    Idiff = clamp(Idiff, 0.0, 1.0);

    
    vec4 Ispec = gl_FrontLightProduct[0].specular * pow(max(dot(R,E),0.0),0.3*gl_FrontMaterial.shininess);
    Ispec = clamp(Ispec, 0.0, 1.0);
   
    intensity = quantize(intensity,levels);
    
    gl_FragColor = gl_FrontLightModelProduct.sceneColor + (Iamb + Idiff + Ispec) * intensity;
}