float hash( float n ){
    return fract(sin(n)*43758.5453);
}

float noise( vec2 uv ){
    vec3 x = vec3(uv, 0);

    vec3 p = floor(x);
    vec3 f = fract(x);
    
    f       = f*f*(3.0-2.0*f);
    float n = p.x + p.y*57.0 + 113.0*p.z;
    
    return mix(mix(mix( hash(n+0.0), hash(n+1.0),f.x),
                   mix( hash(n+57.0), hash(n+58.0),f.x),f.y),
               mix(mix( hash(n+113.0), hash(n+114.0),f.x),
                   mix( hash(n+170.0), hash(n+171.0),f.x),f.y),f.z);
}

mat2 m = mat2(0.8,0.6,-0.6,0.8);

float fbm(vec2 p)
{
    float f = 0.0;
    f += 0.5000*noise( p ); p*=m*2.02;
    f += 0.2500*noise( p ); p*=m*2.03;
    f += 0.1250*noise( p ); p*=m*2.01;
    f += 0.0625*noise( p );
    f /= 0.9375;
    return f;
}

vec3 voronoi( in vec2 x )
{
    ivec2 p = ivec2(floor( x ));
    vec2 f = fract(x);

    ivec2 mb = ivec2(0);
    vec2 mr = vec2(0.0);
    vec2 mg = vec2(0.0);

    float md = 8.0;
    for(int j=-1; j<=1; ++j)
    for(int i=-1; i<=1; ++i)
    {
        ivec2 b = ivec2( i, j );
        vec2  r = vec2( b ) + noise( p + b ) - f;
        vec2 g = vec2(float(i),float(j));
		vec2 o = vec2(noise( vec2(p) + g ));
        float d = length(r);

        if( d<md )
        {
            md = d;
            mr = r;
            mg = g;
        }
    }

    md = 8.0;
    for(int j=-2; j<=2; ++j)
    for(int i=-2; i<=2; ++i)
    {
        ivec2 b = ivec2( i, j );
        vec2 r = vec2( b ) + noise( p + b ) - f;


        if( length(r-mr)>0.00001 )
        md = min( md, dot( 0.5*(mr+r), normalize(r-mr) ) );
    }
    return vec3( md, mr );
}

vec2 tr(vec2 p)
{
 	p = -1.0+2.0*(p/resolution.xy);
    p.x *= resolution.x/resolution.y;
    return p;
}
